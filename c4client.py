import socket
from c4 import *

HOST = "127.0.0.1"
PORT = 65432


def send_message(sock, message): #this section sets up the mechanism for the client to send results to the server
    sock.sendall((message + "\n").encode())


def receive_message(sock): #this section sets up the mechanism for the client to receive messages from the server
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1024)
        if not chunk:
            return ""
        data += chunk
    return data.decode().strip()


# CHANGED: added helper to print scores
def print_scores(score_x, score_o): #this function leverages print mechanisms to print out player scores
    print()
    print("Current Score")
    print(f"Player X: {score_x}")
    print(f"Player O: {score_o}")
    print()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #this statement connects client to server the same way we learned in an older pset
        s.connect((HOST, PORT))
        print_banner("CONNECTED TO CONNECT 4 SERVER AS PLAYER O")

        score_x = 0 #scores initialized at zero, will be incremented over time
        score_o = 0

        while True:  # CHANGED: outer loop for multiple rounds
            board = create_board() #board is an object that we defined in c4.py
            current_piece = "X"

            while True:
                if current_piece == "X":
                    print("Waiting for Player X move...")
                    data = receive_message(s) #we can use the message sent from server throughout the rest of the code logic after this line

                    if data == "":
                        print("Server disconnected.")
                        return

                    if data.startswith("SCORES "):
                        parts = data.split()
                        score_x = int(parts[1])
                        score_o = int(parts[2])
                        print_scores(score_x, score_o)
                        continue

                    if data == "NEW_GAME":
                        continue

                    if data.startswith("MOVE "):
                        col = int(data.split()[1])
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, "X")

                    elif data.startswith("RESULT "):
                        parts = data.split()
                        result = parts[1]
                        score_x = int(parts[2])
                        score_o = int(parts[3])

                        print_board(board)
                        print_scores(score_x, score_o)

                        if result == "DRAW": #result is part of the game logic 
                            print_banner("IT'S A DRAW")
                        else:
                            print_banner(f"PLAYER {result} WINS")
                        break

                    elif data.startswith("REPLAY "):
                        # should not happen here, but safe to ignore
                        continue

                else:
                    print_scores(score_x, score_o)
                    print_board(board)
                    print("Your turn (Player O).")

                    col = get_player_input(board, "O")
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, "O")

                    send_message(s, f"MOVE {col}")

                    if check_win(board, current_piece):
                        # local board update only; server still decides official result
                        pass

                current_piece = "O" if current_piece == "X" else "X"

            # CHANGED: wait for replay decision from server
            replay_message = receive_message(s)

            if replay_message == "":
                print("Server disconnected.")
                return

            if replay_message.startswith("REPLAY "):
                choice = replay_message.split()[1]
                if choice == "y":
                    print_banner("STARTING NEW GAME")
                    continue
                else:
                    print_banner("FINAL SCORES")
                    print_scores(score_x, score_o)
                    print("Game session ended.")
                    break


if __name__ == "__main__":
    main()
