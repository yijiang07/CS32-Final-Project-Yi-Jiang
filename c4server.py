import socket
from c4 import *
from c4ui import Connect4UI

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

        print("Connect4 Server started. Waiting for Player O...")
        conn, addr = s.accept()
        print("Player O connected from", addr)

        with conn:
            board = create_board()
            current_piece = "X"

            ui = Connect4UI()
            ui.draw_board(board)
            ui.show_message("Server / Player X")

            while True:
                print_board(board)
                ui.draw_board(board)

                if current_piece == "X":
                    ui.show_message("Player X turn")
                    col = get_player_input(board, "X")
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, "X")
                    send_message(conn, str(col))
                else:
                    ui.show_message("Waiting for Player O move")
                    print("Waiting for Player O move...")
                    data = receive_message(conn)

                    if data == "":
                        break

                    col = int(data)
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, "O")

                ui.draw_board(board)

                if check_win(board, current_piece):
                    print_board(board)
                    ui.draw_board(board)
                    print(f"Player {current_piece} wins!")
                    ui.show_message(f"Player {current_piece} wins!")
                    send_message(conn, "GAME_OVER")
                    input("Press Enter to close the server window...")
                    break

                if board_full(board):
                    print_board(board)
                    ui.draw_board(board)
                    print("It's a draw!")
                    ui.show_message("Draw!")
                    send_message(conn, "GAME_OVER")
                    input("Press Enter to close the server window...")
                    break

                current_piece = "O" if current_piece == "X" else "X"

            ui.close()
            print("Game over.")


if __name__ == "__main__":
    main()
