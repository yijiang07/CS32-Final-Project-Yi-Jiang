import socket
from c4 import *

HOST = "127.0.0.1"
PORT = 65432


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


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print_banner("CONNECTED TO CONNECT 4 SERVER AS PLAYER O")  # CHANGED

        board = create_board()
        current_piece = "X"

        while True:
            if current_piece == "X":
                print("Waiting for Player X move...")  # CHANGED
                data = receive_message(s)

                if data == "":
                    print("Server disconnected.")
                    break

                if data == "GAME_OVER":
                    break

                col = int(data)
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, "X")

            else:
                print_board(board)
                print("Your turn (Player O).")  # CHANGED

                col = get_player_input(board, "O")
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, "O")

                send_message(s, str(col))

            if check_win(board, current_piece):
                print_board(board)
                print_banner(f"PLAYER {current_piece} WINS")  # CHANGED
                break

            if board_full(board):
                print_board(board)
                print_banner("IT'S A DRAW")  # CHANGED
                break

            current_piece = "O" if current_piece == "X" else "X"

        print("Disconnected.")


if __name__ == "__main__":
    main()
