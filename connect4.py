ROWS = 6
COLS = 7
EMPTY = "."

def create_board():
    board = []
    for i in range(ROWS):
        row = []
        for j in range(COLS):
            row.append(EMPTY)
        board.append(row)
    return board


def print_board(board):
    print()
    for row in board:
        print(" ".join(row))
    print("1 2 3 4 5 6 7")
    print()


def is_valid_column(board, col):
    if col < 0 or col >= COLS:
        return False
    return board[0][col] == EMPTY


def get_next_open_row(board, col):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row
    return None


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def board_full(board):
    for col in range(COLS):
        if board[0][col] == EMPTY:
            return False
    return True


def check_win(board, piece):
    # Horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            if (
                board[row][col] == piece and
                board[row][col + 1] == piece and
                board[row][col + 2] == piece and
                board[row][col + 3] == piece):

                return True

    # Vertical
    for row in range(ROWS - 3):
        for col in range(COLS):
            if (
                board[row][col] == piece and
                board[row + 1][col] == piece and
                board[row + 2][col] == piece and
                board[row + 3][col] == piece
            ):
                return True

    # Diagonal down-right
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if (
                board[row][col] == piece and
                board[row + 1][col + 1] == piece and
                board[row + 2][col + 2] == piece and
                board[row + 3][col + 3] == piece
            ):
                return True

    # Diagonal up-right
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if (
                board[row][col] == piece and
                board[row - 1][col + 1] == piece and
                board[row - 2][col + 2] == piece and
                board[row - 3][col + 3] == piece
            ):
                return True

    return False


def get_player_input(board, player_piece):
    while True:
        choice = input(f"Player {player_piece}, choose a column (1-7): ")

        if not choice.isdigit():
            print("Please enter a number from 1 to 7.")
            continue

        col = int(choice) - 1

        if not is_valid_column(board, col):
            print("That column is invalid or full. Try again.")
            continue

        return col


def play_game():
    board = create_board()
    current_piece = "X"

    print("Welcome to Connect 4!")
    print("Get 4 pieces in a row horizontally, vertically, or diagonally.")

    while True:
        print_board(board)

        col = get_player_input(board, current_piece)
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, current_piece)

        if check_win(board, current_piece):
            print_board(board)
            print(f"Player {current_piece} wins!")
            break

        if board_full(board):
            print_board(board)
            print("It's a draw!")
            break

        if current_piece == "X":
            current_piece = "O"
        else:
            current_piece = "X"


if __name__ == "__main__":
    play_game()
