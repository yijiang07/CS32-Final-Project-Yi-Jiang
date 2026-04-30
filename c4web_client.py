"""
c4web_client.py — Flask web UI for Player O.

Does NOT modify any game logic. Imports from c4.py, uses the same TCP
protocol as c4client.py.

If Player X is on a different machine, change SERVER_HOST to their IP.
"""
import select
import socket
import threading
from flask import Flask, render_template, jsonify, request

from c4 import (
    create_board,
    get_next_open_row,
    drop_piece,
    is_valid_column,
)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 65432
WEB_PORT = 5001

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


def data_available(sock, timeout=2.0):
    """Return True if the socket has data ready to read within `timeout` seconds."""
    ready, _, _ = select.select([sock], [], [], timeout)
    return bool(ready)


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


def apply_result(parts):
    with state_lock:
        state["score_x"] = int(parts[2])
        state["score_o"] = int(parts[3])
        state["result"] = parts[1]
        state["phase"] = "game_over"


def client_loop(sock):
    """
    Fix summary:
    - NEW_GAME now explicitly resets the board so O's screen clears cleanly.
    - After applying X's MOVE, we use select() to check whether the server
      immediately sent a RESULT (win/draw). select() returns in microseconds
      when data is already in the buffer, and waits up to 2 s otherwise —
      long enough to be reliable on any network, fast enough to feel instant.
      No futile move from O is ever required.
    """
    while True:
        with state_lock:
            state["board"] = create_board()
            state["current_piece"] = "X"
            state["result"] = ""
            state["phase"] = "their_turn"

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
                    # Explicitly clear the board so O's screen resets
                    with state_lock:
                        state["board"] = create_board()
                        state["result"] = ""
                        state["current_piece"] = "X"
                        state["phase"] = "their_turn"
                    continue

                if data.startswith("MOVE "):
                    col = int(data.split()[1])
                    with state_lock:
                        row = get_next_open_row(state["board"], col)
                        drop_piece(state["board"], row, col, "X")

                    # Use select() to check if RESULT is already in the buffer.
                    # If X's move was a winner the server sends RESULT immediately,
                    # so select() returns True right away. If not, we time out
                    # after 2 s and let O take their turn normally.
                    if data_available(sock, timeout=2.0):
                        next_msg = receive_message(sock)
                        if next_msg == "":
                            with state_lock:
                                state["phase"] = "disconnected"
                            return
                        if next_msg.startswith("RESULT "):
                            apply_result(next_msg.split())
                            break
                        # Unexpected message — handle it gracefully
                        if next_msg.startswith("SCORES "):
                            parts = next_msg.split()
                            with state_lock:
                                state["score_x"] = int(parts[1])
                                state["score_o"] = int(parts[2])
                    # Either no data within 2 s, or a non-RESULT message —
                    # fall through and let O take their turn.

                elif data.startswith("RESULT "):
                    apply_result(data.split())
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

        # Replay decision from server
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
        print(f"[TCP] Could not connect to {SERVER_HOST}:{SERVER_PORT}.")
        with state_lock:
            state["phase"] = "disconnected"
    except Exception as e:
        print(f"[TCP] Error: {e}")
        with state_lock:
            state["phase"] = "disconnected"


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
    return jsonify({"ok": True})


if __name__ == "__main__":
    t = threading.Thread(target=tcp_client_thread, daemon=True)
    t.start()
    print(f"[WEB] Open http://localhost:{WEB_PORT} in your browser (Player O)")
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, use_reloader=False)
