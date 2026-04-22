from socket import create_new_socket
from c4 import *
from c4ui import Connect4UI  # CHANGED: added UI

HOST = '127.0.0.1'
PORT = 65432


def main():
    with create_new_socket() as s:
        s.bind(HOST, PORT)
        s.listen()

        print("Connect4 Server started. Waiting for Player O...")
        conn, addr = s.accept()
        print("Player O connected from", addr)

        with conn:
            board = create_board()
            current_piece = "X"

            ui = Connect4UI()  # CHANGED: create graphical UI
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

                    conn.sendall(str(col))  # send move to client

                else:
                    ui.show_message("Waiting for Player O move")
                    print("Waiting for Player O move...")
                    data = conn.recv()

                    if data == '':
                        break

                    col = int(data)
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, "O")

                ui.draw_board(board)  # CHANGED: update GUI after move

                if check_win(board, current_piece):
                    print_board(board)
                    ui.draw_board(board)

                    if current_piece == "X":
                        print("Player X wins!")
                        ui.show_message("Player X wins!")
                    else:
                        print("Player O wins!")
                        ui.show_message("Player O wins!")

                    conn.sendall("GAME_OVER")
                    input("Press Enter to close the server window...")
                    break

                if board_full(board):
                    print_board(board)
                    ui.draw_board(board)
                    print("It's a draw!")
                    ui.show_message("Draw!")
                    conn.sendall("GAME_OVER")
                    input("Press Enter to close the server window...")
                    break

                current_piece = "O" if current_piece == "X" else "X"

            ui.close()
            print("Game over.")


if __name__ == "__main__":
    main()
