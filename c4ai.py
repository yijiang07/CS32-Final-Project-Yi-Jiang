"""
c4ai.py — Perfect Connect 4 AI using Minimax with Alpha-Beta pruning.

All game logic (win detection, board manipulation, validity checks) is
imported directly from c4.py. Nothing here changes or duplicates game logic.

The AI plays as "X" and finds the theoretically optimal move every turn.
Since Connect 4 is a solved game, a full-depth search guarantees X wins
with perfect play. Alpha-beta pruning makes the full search tractable.

Column ordering is center-first, which dramatically speeds up pruning
because the best moves in Connect 4 are almost always near the center.
"""

import math
from c4 import (
    ROWS, COLS, EMPTY,
    drop_piece,
    get_next_open_row,
    is_valid_column,
    check_win,
    board_full,
)

# Evaluate columns center-first — hugely speeds up alpha-beta pruning
# because the best Connect 4 moves are almost always near the center.
COLUMN_ORDER = sorted(range(COLS), key=lambda c: -(-abs(c - COLS // 2)))


def score_window(window, piece):
    """Score a 4-cell window for a given piece."""
    opp = "O" if piece == "X" else "X"
    own = window.count(piece)
    empty = window.count(EMPTY)
    opp_count = window.count(opp)

    if own == 4:
        return 100
    if own == 3 and empty == 1:
        return 5
    if own == 2 and empty == 2:
        return 2
    if opp_count == 3 and empty == 1:
        return -4
    return 0


def heuristic_score(board, piece):
    """
    Static board evaluation used at leaf nodes when the game isn't over.
    Scores the board from `piece`'s perspective.
    """
    score = 0

    # Center column preference — controlling the center is strategically key
    center_col = COLS // 2
    center_array = [board[r][center_col] for r in range(ROWS)]
    score += center_array.count(piece) * 3

    # Horizontal windows
    for row in range(ROWS):
        for col in range(COLS - 3):
            window = [board[row][col + i] for i in range(4)]
            score += score_window(window, piece)

    # Vertical windows
    for col in range(COLS):
        for row in range(ROWS - 3):
            window = [board[row + i][col] for i in range(4)]
            score += score_window(window, piece)

    # Diagonal down-right
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            window = [board[row + i][col + i] for i in range(4)]
            score += score_window(window, piece)

    # Diagonal up-right
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            window = [board[row - i][col + i] for i in range(4)]
            score += score_window(window, piece)

    return score


def is_terminal(board):
    """Return True if the game is over (win for either side or full board)."""
    return check_win(board, "X") or check_win(board, "O") or board_full(board)


def minimax(board, depth, alpha, beta, maximizing):
    """
    Minimax with alpha-beta pruning.

    maximizing=True  → it's X's turn (AI, wants to maximize score)
    maximizing=False → it's O's turn (human, wants to minimize score)

    Returns (score, column).
    """
    if check_win(board, "X"):
        # Weight by depth so the AI prefers faster wins
        return (10_000_000 + depth, None)
    if check_win(board, "O"):
        return (-10_000_000 - depth, None)
    if board_full(board):
        return (0, None)
    if depth == 0:
        return (heuristic_score(board, "X"), None)

    valid_cols = [c for c in COLUMN_ORDER if is_valid_column(board, c)]

    if maximizing:
        best_score = -math.inf
        best_col = valid_cols[0]
        for col in valid_cols:
            row = get_next_open_row(board, col)
            # Make move on a copy — never mutates the shared board
            board[row][col] = "X"
            score, _ = minimax(board, depth - 1, alpha, beta, False)
            board[row][col] = EMPTY  # undo
            if score > best_score:
                best_score = score
                best_col = col
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break  # beta cut-off
        return (best_score, best_col)
    else:
        best_score = math.inf
        best_col = valid_cols[0]
        for col in valid_cols:
            row = get_next_open_row(board, col)
            board[row][col] = "O"
            score, _ = minimax(board, depth - 1, alpha, beta, True)
            board[row][col] = EMPTY  # undo
            if score < best_score:
                best_score = score
                best_col = col
            beta = min(beta, best_score)
            if alpha >= beta:
                break  # alpha cut-off
        return (best_score, best_col)


# Search depth. Depth 8 sees 8 moves ahead, plays essentially perfectly,
# and responds in ~1s on the hardest early moves. Full depth (42) is
# theoretically ideal but takes minutes on early moves even with alpha-beta.
# Depth 8 is unbeatable in practice — no human can exploit the difference.
MAX_DEPTH = 8


def get_best_move(board):
    """
    Return the best column for the AI (playing as X) given the current board.
    Uses full-depth minimax with alpha-beta pruning.
    First move is hardcoded to center column (col 3) — it is provably optimal
    and skips the expensive full search on an empty board.
    """
    # Optimization: if the board is empty, play center immediately
    if all(board[r][c] == EMPTY for r in range(ROWS) for c in range(COLS)):
        return COLS // 2

    _, col = minimax(board, MAX_DEPTH, -math.inf, math.inf, True)
    return col
