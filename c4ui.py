import tkinter as tk


class Connect4UI:
    # CHANGED: graphical UI for drawing the board
    def __init__(self, rows=6, cols=7, cell_size=90):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = 10

        width = self.cols * self.cell_size
        height = self.rows * self.cell_size

        self.root = tk.Tk()
        self.root.title("Connect 4")

        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg="royal blue",
            highlightthickness=0
        )
        self.canvas.pack()

    def draw_board(self, board):
        # CHANGED: redraw board every time game state changes
        self.canvas.delete("all")

        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * self.cell_size + self.margin
                y1 = row * self.cell_size + self.margin
                x2 = (col + 1) * self.cell_size - self.margin
                y2 = (row + 1) * self.cell_size - self.margin

                piece = board[row][col]

                if piece == "X":
                    color = "red"
                elif piece == "O":
                    color = "yellow"
                else:
                    color = "white"

                self.canvas.create_oval(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="black",
                    width=2
                )

        self.root.update_idletasks()
        self.root.update()

    def show_message(self, message):
        # CHANGED: window title updates for turn / winner / draw
        self.root.title("Connect 4 - " + message)
        self.root.update_idletasks()
        self.root.update()

    def close(self):
        self.root.destroy()
