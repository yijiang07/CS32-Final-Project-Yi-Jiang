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


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print_banner("CONNECT 4 SERVER STARTED")  # CHANGED
        print("Waiting for Player O...")
        conn, addr = s.accept()
        print("Player O connected from", addr)

        with conn:
            board = create_board()
            current_piece = "X"

            while True:
                print_board(board)

                if current_piece == "X":
                    print("Your turn (Player X).")  # CHANGED
                    col = get_player_input(board, "X")
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, "X")
                    send_message(conn, str(col))
                else:
                    print("Waiting for Player O move...")  # CHANGED
                    data = receive_message(conn)

                    if data == "":
                        print("Client disconnected.")
                        break

                    col = int(data)
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, "O")

                if check_win(board, current_piece):
                    print_board(board)
                    print_banner(f"PLAYER {current_piece} WINS")  # CHANGED
                    send_message(conn, "GAME_OVER")
                    break

                if board_full(board):
                    print_board(board)
                    print_banner("IT'S A DRAW")  # CHANGED
                    send_message(conn, "GAME_OVER")
                    break

                current_piece = "O" if current_piece == "X" else "X"

            print("Game over.")


if __name__ == "__main__":
    main()
