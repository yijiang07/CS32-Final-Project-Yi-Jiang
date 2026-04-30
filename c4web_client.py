"""
c4web_client.py — Flask web UI for Player O.

This file does NOT modify any game logic. It imports functions from c4.py
and uses the same TCP protocol as c4client.py:
   SCORES <x> <o>, NEW_GAME, MOVE <col>, RESULT <X|O|DRAW> <x> <o>, REPLAY <y|n>

Run this on Player O's machine, then open http://localhost:5001 in a browser.
Player X must already be running c4web_server.py.

If Player X is on a different machine, change SERVER_HOST below to their IP.
"""
import socket
import threading
from flask import Flask, render_template, jsonify, request

from c4 import (
    create_board,
    get_next_open_row,
    drop_piece,
    is_valid_column,
)

# ----- Network config -----
SERVER_HOST = "127.0.0.1"   # <-- change to Player X's IP if on a different machine
SERVER_PORT = 65432
WEB_PORT = 5001

# ----- Shared state -----
state_lock = threading.Lock()
state = {
    "board": create_board(),
    "score_x": 0,
    "score_o": 0,
    "current_piece": "X",
    "phase": "waiting_for_opponent",
    "result": "",
}

pending_move_o = {"col": None}
pending_move_lock = threading.Lock()
move_event = threading.Event()


# --- TCP message helpers (identical wire format to c4client.py) ---
def send_message(sock, message):
    sock.sendall((message + "\n").encode())


def receive_message(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1024)
        if not chunk:
            return ""
        data += chunk
    return data.decode().strip()


def wait_for_web_move():
    while True:
        move_event.wait()
        move_event.clear()
        with pending_move_lock:
            col = pending_move_o["col"]
            pending_move_o["col"] = None
        if col is None:
            continue
        with state_lock:
            if is_valid_column(state["board"], col):
                return col


def client_loop(sock):
    """Mirrors c4client.py's main loop: handles SCORES / NEW_GAME / MOVE /
    RESULT / REPLAY messages from the server, and sends MOVE messages from
    the web UI."""
    while True:
        with state_lock:
            state["board"] = create_board()
            state["current_piece"] = "X"
            state["result"] = ""
            state["phase"] = "their_turn"  # X always starts

        while True:
            with state_lock:
                current_piece = state["current_piece"]

            if current_piece == "X":
                with state_lock:
                    state["phase"] = "their_turn"
                data = receive_message(sock)
                if data == "":
                    with state_lock:
                        state["phase"] = "disconnected"
                    return

                if data.startswith("SCORES "):
                    parts = data.split()
                    with state_lock:
                        state["score_x"] = int(parts[1])
                        state["score_o"] = int(parts[2])
                    continue

                if data == "NEW_GAME":
                    continue

                if data.startswith("MOVE "):
                    col = int(data.split()[1])
                    with state_lock:
                        row = get_next_open_row(state["board"], col)
                        drop_piece(state["board"], row, col, "X")

                    # UX improvement: peek for an immediate RESULT so O sees
                    # the win/draw banner without having to make a futile move.
                    # Game logic is untouched — we just read one more message
                    # if the server sent one.
                    sock.settimeout(0.4)
                    try:
                        peek = receive_message(sock)
                    except socket.timeout:
                        peek = None
                    finally:
                        sock.settimeout(None)

                    if peek and peek.startswith("RESULT "):
                        parts = peek.split()
                        result = parts[1]
                        with state_lock:
                            state["score_x"] = int(parts[2])
                            state["score_o"] = int(parts[3])
                            state["result"] = result
                            state["phase"] = "game_over"
                        break
                    elif peek == "":
                        with state_lock:
                            state["phase"] = "disconnected"
                        return
                    elif peek is not None:
                        # Unexpected message — handle defensively by re-queueing logic
                        # (shouldn't happen with current protocol, but stay safe)
                        if peek.startswith("SCORES "):
                            parts = peek.split()
                            with state_lock:
                                state["score_x"] = int(parts[1])
                                state["score_o"] = int(parts[2])

                elif data.startswith("RESULT "):
                    parts = data.split()
                    result = parts[1]
                    with state_lock:
                        state["score_x"] = int(parts[2])
                        state["score_o"] = int(parts[3])
                        state["result"] = result
                        state["phase"] = "game_over"
                    break

                elif data.startswith("REPLAY "):
                    continue
            else:
                with state_lock:
                    state["phase"] = "your_turn"
                col = wait_for_web_move()
                with state_lock:
                    row = get_next_open_row(state["board"], col)
                    drop_piece(state["board"], row, col, "O")
                send_message(sock, f"MOVE {col}")

            with state_lock:
                state["current_piece"] = "O" if current_piece == "X" else "X"

        # --- replay decision comes from server ---
        replay_msg = receive_message(sock)
        if replay_msg == "":
            with state_lock:
                state["phase"] = "disconnected"
            return
        if replay_msg.startswith("REPLAY "):
            choice = replay_msg.split()[1]
            if choice == "y":
                continue
            else:
                with state_lock:
                    state["phase"] = "session_ended"
                return


def tcp_client_thread():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_HOST, SERVER_PORT))
        print(f"[TCP] Connected to Player X at {SERVER_HOST}:{SERVER_PORT}")
        with state_lock:
            state["phase"] = "their_turn"
        with sock:
            client_loop(sock)
    except ConnectionRefusedError:
        print(f"[TCP] Could not connect to {SERVER_HOST}:{SERVER_PORT}. "
              f"Is Player X running c4web_server.py?")
        with state_lock:
            state["phase"] = "disconnected"
    except Exception as e:
        print(f"[TCP] Error: {e}")
        with state_lock:
            state["phase"] = "disconnected"


# ----- Flask app -----
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("board.html", player="O")


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
        pending_move_o["col"] = col
    move_event.set()
    return jsonify({"ok": True})


@app.route("/replay", methods=["POST"])
def post_replay():
    # Player O does not control replay; ignore politely.
    return jsonify({"ok": True})


if __name__ == "__main__":
    t = threading.Thread(target=tcp_client_thread, daemon=True)
    t.start()
    print(f"[WEB] Open http://localhost:{WEB_PORT} in your browser (Player O)")
    app.run(host="127.0.0.1", port=WEB_PORT, debug=False, use_reloader=False)
