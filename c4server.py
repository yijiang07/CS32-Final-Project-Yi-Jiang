import socket
from c4 import *

HOST = "127.0.0.1"
PORT = 65432


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


# CHANGED: added helper to ask whether to play again
def ask_play_again():
    while True:
        choice = input("Play again? (y/n): ").strip().lower()
        if choice in ["y", "n"]:
            return choice
        print("Please enter y or n.")


# CHANGED: added helper to print scores
def print_scores(score_x, score_o):
    print()
    print("Current Score")
    print(f"Player X: {score_x}")
    print(f"Player O: {score_o}")
    print()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT)) #binds the server to the client
        s.listen()
#the rest of the code works in essence identical to the client code, but note that since the server is sending its message FIRST, which means we must account for this at some point to make sure that client and server terminals reflect the same info simultaneously.
        print_banner("CONNECT 4 SERVER STARTED")
        print("Waiting for Player O...")
        conn, addr = s.accept()
        print("Player O connected from", addr)

        with conn:
            # CHANGED: score tracking across multiple games
            score_x = 0
            score_o = 0

            while True:  # CHANGED: outer loop for replay / multiple rounds
                board = create_board()
                current_piece = "X"
                game_result = ""

                print_banner("NEW GAME")
                print_scores(score_x, score_o)
                send_message(conn, f"SCORES {score_x} {score_o}")
                send_message(conn, "NEW_GAME")

                while True:
                    print_scores(score_x, score_o)
                    print_board(board)

                    if current_piece == "X":
                        print("Your turn (Player X).")
                        col = get_player_input(board, "X")
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, "X")
                        send_message(conn, f"MOVE {col}")
                    else:
                        print("Waiting for Player O move...")
                        data = receive_message(conn)

                        if data == "":
                            print("Client disconnected.")
                            return

                        if data.startswith("MOVE "):
                            col = int(data.split()[1])
                            row = get_next_open_row(board, col)
                            drop_piece(board, row, col, "O")

                    if check_win(board, current_piece):
                        print_board(board)
                        print_banner(f"PLAYER {current_piece} WINS")

                        if current_piece == "X":
                            score_x += 1
                            game_result = "X"
                        else:
                            score_o += 1
                            game_result = "O"

                        send_message(conn, f"RESULT {game_result} {score_x} {score_o}")
                        break

                    if board_full(board):
                        print_board(board)
                        print_banner("IT'S A DRAW")
                        game_result = "DRAW"
                        send_message(conn, f"RESULT DRAW {score_x} {score_o}")
                        break

                    current_piece = "O" if current_piece == "X" else "X"

                # CHANGED: ask server player if they want to play again
                print_scores(score_x, score_o)
                choice = ask_play_again()

                if choice == "y":
                    send_message(conn, "REPLAY y")
                    continue
                else:
                    send_message(conn, "REPLAY n")
                    print_banner("FINAL SCORES")
                    print_scores(score_x, score_o)
                    print("Game session ended.")
                    break


if __name__ == "__main__":
    main()
