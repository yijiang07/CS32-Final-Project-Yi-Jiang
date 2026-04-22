import random  # CHANGED: added for computer opponent

ROWS = 6
COLS = 7
EMPTY = "."


def create_board():  # creating a 2 dimensional connect 4 board
    board = []
    for i in range(ROWS):
        row = []
        for j in range(COLS):
            row.append(EMPTY)
        board.append(row)
    return board


def print_board(board):  # prints the board to the terminal
    # CHANGED: improved UI formatting
    print()
    print("  1 2 3 4 5 6 7")
    for row_num in range(ROWS):
        print(str(row_num + 1) + " " + " ".join(board[row_num]))
    print()


def is_valid_column(board, col):  # checks to make sure that the column that the player put the piece in is valid
    if col < 0 or col >= COLS:
        return False
    return board[0][col] == EMPTY


def get_next_open_row(board, col):  # gets the next open row in the column the player chose
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row
    return None


def drop_piece(board, row, col, piece):  # drops the piece in the column the player chose
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
                board[row][col + 3] == piece
            ):
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


# CHANGED: added helper function for menu selection
def choose_game_mode():
    while True:
        print("Choose a game mode:")
        print("1. Player vs Player")
        print("2. Player vs Computer")
        choice = input("Enter 1 or 2: ")

        if choice == "1":
            return "pvp"
        if choice == "2":
            return "ai"

        print("Invalid choice. Please enter 1 or 2.")


# CHANGED: added simple AI extension
def get_ai_move(board):
    valid_columns = []
    for col in range(COLS):
        if is_valid_column(board, col):
            valid_columns.append(col)

    return random.choice(valid_columns)


# CHANGED: added helper function to switch turns
def switch_piece(current_piece):
    if current_piece == "X":
        return "O"
    return "X"


# CHANGED: added score display helper for better UI
def print_score(score_x, score_o):
    print()
    print("Current Score")
    print(f"Player X: {score_x}")
    print(f"Player O: {score_o}")
    print()


# CHANGED: added replay prompt
def play_again():
    while True:
        choice = input("Would you like to play again? (y/n): ").lower()
        if choice == "y":
            return True
        if choice == "n":
            return False
        print("Please enter y or n.")


def play_game():
    # CHANGED: added mode selection and score tracking
    mode = choose_game_mode()
    score_x = 0
    score_o = 0

    print("Welcome to Connect 4!")
    print("Get 4 pieces in a row horizontally, vertically, or diagonally.")

    while True:
        board = create_board()
        current_piece = "X"

        while True:
            print_score(score_x, score_o)  # CHANGED: improved UI
            print_board(board)

            # CHANGED: support computer opponent
            if mode == "ai" and current_piece == "O":
                col = get_ai_move(board)
                print(f"Computer chooses column {col + 1}")
            else:
                col = get_player_input(board, current_piece)

            row = get_next_open_row(board, col)
            drop_piece(board, row, col, current_piece)

            if check_win(board, current_piece):
                print_board(board)

                if mode == "ai" and current_piece == "O":
                    print("Computer wins!")
                else:
                    print(f"Player {current_piece} wins!")

                if current_piece == "X":
                    score_x += 1
                else:
                    score_o += 1
                break

            if board_full(board):
                print_board(board)
                print("It's a draw!")
                break

            current_piece = switch_piece(current_piece)

        if not play_again():
            print("Final scores:")
            print_score(score_x, score_o)
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    play_game()
