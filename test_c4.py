# test_connect4.py

from connect4 import create_board, drop_piece, check_win, get_next_open_row

def test_horizontal_win():
    board = create_board()
    row = 5
    for col in range(4):
        drop_piece(board, row, col, "X")
    assert check_win(board, "X") == True

def test_vertical_win():
    board = create_board()
    col = 0
    for row in range(2, 6):
        drop_piece(board, row, col, "O")
    assert check_win(board, "O") == True

def test_down_right_diagonal_win():
    board = create_board()
    drop_piece(board, 2, 0, "X")
    drop_piece(board, 3, 1, "X")
    drop_piece(board, 4, 2, "X")
    drop_piece(board, 5, 3, "X")
    assert check_win(board, "X") == True

def test_up_right_diagonal_win():
    board = create_board()
    drop_piece(board, 5, 0, "O")
    drop_piece(board, 4, 1, "O")
    drop_piece(board, 3, 2, "O")
    drop_piece(board, 2, 3, "O")
    assert check_win(board, "O") == True

def test_next_open_row():
    board = create_board()
    col = 3
    assert get_next_open_row(board, col) == 5
    drop_piece(board, 5, col, "X")
    assert get_next_open_row(board, col) == 4

def run_tests():
    test_horizontal_win()
    test_vertical_win()
    test_down_right_diagonal_win()
    test_up_right_diagonal_win()
    test_next_open_row()
    print("All tests passed!")

if __name__ == "__main__":
    run_tests()
