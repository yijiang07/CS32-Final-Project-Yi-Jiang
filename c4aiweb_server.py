"""
c4web_ai_server.py — Flask web UI for Impossible Mode.

The AI plays as Player X automatically using minimax and alpha-beta pruning, which is specified in c4ai.py.
The human plays as Player O in the browser.

All the main game logic is unchanged, but this file only wires the AI's get_best_move()
into the same game loop used by c4web_server.py.

The way it works is you just run python3 c4web_ai_server.py
Then open http://localhost:5002 in your browser, it should come up as a pop up. Read the ReadME for more instructions if not clear.
"""
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
from c4ai import get_best_move

WEB_PORT = 5002

state_lock = threading.Lock()
state = {
    "board": create_board(),
    "score_x": 0,
    "score_o": 0,
    "phase": "ai_thinking",
    "result": "",
    "game_id": 0,   # incremented each new round so the UI knows to clear the board
}

pending_move = {"col": None}
pending_move_lock = threading.Lock()
move_event = threading.Event()


def wait_for_human_move():
    while True:
        move_event.wait()
        move_event.clear()
        with pending_move_lock:
            col = pending_move["col"]
            pending_move["col"] = None
        if col is None:
            continue
        with state_lock:
            if is_valid_column(state["board"], col):
                return col


replay_pending = {"choice": None}
replay_event = threading.Event()


def wait_for_replay():
    while True:
        replay_event.wait()
        replay_event.clear()
        choice = replay_pending["choice"]
        replay_pending["choice"] = None
        if choice in ("y", "n"):
            return choice


def ai_game_loop():
    """
    Game loop for AI (X) vs Human (O).
    AI moves are computed in this background thread so Flask stays responsive.
    Human moves arrive via /move endpoint and the move_event.
    """
    while True:
        # Reset state and broadcast the empty board BEFORE the AI thinks,
        # so the browser clears the old board immediately.
        with state_lock:
            state["board"] = create_board()
            state["result"] = ""
            state["phase"] = "ai_thinking"
            state["game_id"] += 1

        while True:
            #  AI's turn (X)
            with state_lock:
                state["phase"] = "ai_thinking"
                board_snapshot = [row[:] for row in state["board"]]

            # Compute best move outside the lock so Flask can still serve /state
            col = get_best_move(board_snapshot)

            with state_lock:
                row = get_next_open_row(state["board"], col)
                drop_piece(state["board"], row, col, "X")

                if check_win(state["board"], "X"):
                    state["score_x"] += 1
                    state["result"] = "X"
                    state["phase"] = "game_over"
                    break

                if board_full(state["board"]):
                    state["result"] = "DRAW"
                    state["phase"] = "game_over"
                    break

            #  Human's turn (O)
            with state_lock:
                state["phase"] = "your_turn"

            col = wait_for_human_move()

            with state_lock:
                row = get_next_open_row(state["board"], col)
                drop_piece(state["board"], row, col, "O")

                if check_win(state["board"], "O"):
                    state["score_o"] += 1
                    state["result"] = "O"
                    state["phase"] = "game_over"
                    break

                if board_full(state["board"]):
                    state["result"] = "DRAW"
                    state["phase"] = "game_over"
                    break

        #  Replay option
        choice = wait_for_replay()
        if choice == "n":
            with state_lock:
                state["phase"] = "session_ended"
            return
        # choice == "y" means that the outer loop resets board


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("board_ai.html")


@app.route("/state")
def get_state():
    with state_lock:
        return jsonify({
            "board": state["board"],
            "score_x": state["score_x"],
            "score_o": state["score_o"],
            "phase": state["phase"],
            "result": state["result"],
            "game_id": state["game_id"],
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
        pending_move["col"] = col
    move_event.set()
    return jsonify({"ok": True})


@app.route("/replay", methods=["POST"])
def post_replay():
    body = request.get_json(silent=True) or {}
    choice = body.get("choice")
    if choice not in ("y", "n"):
        return jsonify({"ok": False, "error": "bad choice"}), 400
    replay_pending["choice"] = choice
    replay_event.set()
    return jsonify({"ok": True})


if __name__ == "__main__":
    t = threading.Thread(target=ai_game_loop, daemon=True)
    t.start()
    print(f"[WEB] Impossible Mode → http://localhost:{WEB_PORT}")
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, use_reloader=False)
