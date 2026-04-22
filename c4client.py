import socket
from c4 import *
from c4ui import Connect4UI

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
        print("Connected to Connect4 Server as Player O")

        board = create_board()
        current_piece = "X"

        ui = Connect4UI()
        ui.draw_board(board)
        ui.show_message("Client / Player O")

        while True:
            if current_piece == "X":
                ui.show_message("Waiting for Player X move")
                data = receive_message(s)

                if data == "":
                    break

                if data == "GAME_OVER":
                    input("Press Enter to close the client window...")
                    break

                col = int(data)
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, "X")

            else:
                print_board(board)
                ui.draw_board(board)
                ui.show_message("Player O turn")

                col = get_player_input(board, "O")
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, "O")

                send_message(s, str(col))

            ui.draw_board(board)

            if check_win(board, current_piece):
                print_board(board)
                ui.draw_board(board)
                print(f"Player {current_piece} wins!")
                ui.show_message(f"Player {current_piece} wins!")
                break

            if board_full(board):
                print_board(board)
                ui.draw_board(board)
                print("It's a draw!")
                ui.show_message("Draw!")
                break

            current_piece = "O" if current_piece == "X" else "X"

        ui.close()
        print("Disconnected.")


if __name__ == "__main__":
    main()
