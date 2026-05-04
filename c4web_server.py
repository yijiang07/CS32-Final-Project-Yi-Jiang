"""
c4web_server.py: This is the flask web UI for Player X.

This file doesn't modify any game logic. It imports functions from c4.py
(create_board, get_next_open_row, drop_piece, check_win, board_full,
is_valid_column) and uses the same TCP protocol as c4server.py:
   SCORES <x> <o>, NEW_GAME, MOVE <col>, RESULT <X|O|DRAW> <x> <o>, REPLAY <y|n>

Run this on Player X's machine, then open http://localhost:5000 in a browser.
Player O runs c4web_client.py on their machine.
"""
import socket
import threading
from flask import Flask, render_template, jsonify, request

from c4 import (
    create_board,
    get_next_open_row,
    drop_piece,
    check_win,
    board_full,
    is_valid_column,
)


TCP_HOST = "0.0.0.0"   # listen on all interfaces so a remote Player O can connect
TCP_PORT = 65432
WEB_PORT = 5000

# this is a Shared state, guarded by a lock
state_lock = threading.Lock()
state = {
    "board": create_board(),
    "score_x": 0,
    "score_o": 0,
    "current_piece": "X",
    "phase": "waiting_for_opponent",  # waiting_for_opponent --> your_turn --> their_turn --> game_over --> session_ended --> disconnected
    "result": "",
}

# Pending move from the web UI for Player X — picked up by the TCP thread
pending_move_x = {"col": None}
pending_move_lock = threading.Lock()
move_event = threading.Event()

# Replay decision from the web UI ("y" or "n")
pending_replay = {"choice": None}
replay_event = threading.Event()

conn_holder = {"conn": None}


# these are the TCP message helpers
def send_message(conn, message):
    conn.sendall((message + "\n").encode())


def receive_message(conn):
    data = b""
    while not data.endswith(b"\n"):
        chunk = conn.recv(1024)
        if not chunk:
            return ""
        data += chunk
    return data.decode().strip()


def wait_for_web_move():
    """Block until the web UI submits a valid column for Player X."""
    while True:
        move_event.wait()
        move_event.clear()
        with pending_move_lock:
            col = pending_move_x["col"]
            pending_move_x["col"] = None
        if col is None:
            continue
        with state_lock:
            if is_valid_column(state["board"], col):
                return col



def wait_for_web_replay():
    """Block until the web UI submits a replay choice."""
    while True:
        replay_event.wait()
        replay_event.clear()
        choice = pending_replay["choice"]
        pending_replay["choice"] = None
        if choice in ("y", "n"):
            return choice


def game_loop(conn):
    """Mirrors the structure of c4server.py's main loop, but pulls X's moves
    from the web UI instead of input(), and sends UI-visible state updates."""
    conn_holder["conn"] = conn

    while True:
        # New game setup, the same messages as c4server.py
        with state_lock:
            state["board"] = create_board()
            state["current_piece"] = "X"
            state["result"] = ""
            state["phase"] = "your_turn"  # X starts
            score_x = state["score_x"]
            score_o = state["score_o"]

        send_message(conn, f"SCORES {score_x} {score_o}")
        send_message(conn, "NEW_GAME")

        while True:
            with state_lock:
                current_piece = state["current_piece"]

            if current_piece == "X":
                with state_lock:
                    state["phase"] = "your_turn"
                col = wait_for_web_move()
                with state_lock:
                    row = get_next_open_row(state["board"], col)
                    drop_piece(state["board"], row, col, "X")
                send_message(conn, f"MOVE {col}")
            else:
                with state_lock:
                    state["phase"] = "their_turn"
                data = receive_message(conn)
                if data == "":
                    with state_lock:
                        state["phase"] = "disconnected"
                    return
                if data.startswith("MOVE "):
                    col = int(data.split()[1])
                    with state_lock:
                        row = get_next_open_row(state["board"], col)
                        drop_piece(state["board"], row, col, "O")

            # these are win/draw checks (same logic as c4server.py)
            with state_lock:
                won = check_win(state["board"], current_piece)
                full = board_full(state["board"])

            if won:
                with state_lock:
                    if current_piece == "X":
                        state["score_x"] += 1
                    else:
                        state["score_o"] += 1
                    state["result"] = current_piece
                    state["phase"] = "game_over"
                    sx, so = state["score_x"], state["score_o"]
                send_message(conn, f"RESULT {current_piece} {sx} {so}")
                break

            if full:
                with state_lock:
                    state["result"] = "DRAW"
                    state["phase"] = "game_over"
                    sx, so = state["score_x"], state["score_o"]
                send_message(conn, f"RESULT DRAW {sx} {so}")
                break

            with state_lock:
                state["current_piece"] = "O" if current_piece == "X" else "X"

        #  this is the replay decision (same protocol as c4server.py)
        choice = wait_for_web_replay()
        if choice == "y":
            send_message(conn, "REPLAY y")
            continue
        else:
            send_message(conn, "REPLAY n")
            with state_lock:
                state["phase"] = "session_ended"
            return


def tcp_server_thread():
    """Accept one Player O connection and run the game loop."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((TCP_HOST, TCP_PORT))
        s.listen()
        print(f"[TCP] Listening on {TCP_HOST}:{TCP_PORT} for Player O…")
        conn, addr = s.accept()
        print(f"[TCP] Player O connected from {addr}")
        with conn:
            with state_lock:
                state["phase"] = "your_turn"
            try:
                game_loop(conn)
            except Exception as e:
                print(f"[TCP] Connection error: {e}")
                with state_lock:
                    state["phase"] = "disconnected"


# setting up the Flask app!
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("board.html", player="X")


@app.route("/state")
def get_state():
    with state_lock:
        return jsonify({
            "board": state["board"],
            "score_x": state["score_x"],
            "score_o": state["score_o"],
            "phase": state["phase"],
            "result": state["result"],
        })


@app.route("/move", methods=["POST"])
def post_move():
    body = request.get_json(silent=True) or {}
    col = body.get("col")
    if not isinstance(col, int):
        return jsonify({"ok": False, "error": "bad column"}), 400
    with state_lock:
        if state["phase"] != "your_turn":
            return jsonify({"ok": False, "error": "not your turn"}), 400
        if not is_valid_column(state["board"], col):
            return jsonify({"ok": False, "error": "invalid column"}), 400
    with pending_move_lock:
        pending_move_x["col"] = col
    move_event.set()
    return jsonify({"ok": True})


@app.route("/replay", methods=["POST"])
def post_replay():
    body = request.get_json(silent=True) or {}
    choice = body.get("choice")
    if choice not in ("y", "n"):
        return jsonify({"ok": False, "error": "bad choice"}), 400
    pending_replay["choice"] = choice
    replay_event.set()
    return jsonify({"ok": True})


if __name__ == "__main__":
    t = threading.Thread(target=tcp_server_thread, daemon=True)
    t.start()
    print(f"[WEB] Open http://localhost:{WEB_PORT} in your browser (Player X)")
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, use_reloader=False)
