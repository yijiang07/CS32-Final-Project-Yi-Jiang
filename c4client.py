from socket import create_new_socket
from c4 import *
from c4ui import Connect4UI  # CHANGED: added UI

HOST = '127.0.0.1'
PORT = 65432


def main():
    with create_new_socket() as s:
        s.connect(HOST, PORT)
        print("Connected to Connect4 Server as Player O")

        board = create_board()
        current_piece = "X"

        ui = Connect4UI()  # CHANGED: create graphical UI
        ui.draw_board(board)
        ui.show_message("Client / Player O")

        while True:
            if current_piece == "X":
                ui.show_message("Waiting for Player X move")
                data = s.recv()

                if data == '':
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

                s.sendall(str(col))

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
