from tkinter import *

from minesweeper import Minesweeper


class MinesweeperGui(object):
    CELL_WIDTH = 16
    CELL_HEIGHT = 16

    number_colors = {
        1: 'blue',
        2: 'green',
        3: 'red'
    }

    def __init__(self, root):
        self.root = root
        root.title("Minesweeper")

        self.header = Label(self.root, text="")
        self.header.grid(row=0)
        self.header.bind("<Button-1>", lambda e: self.init_game())

        self.game = None
        self.canvas = None
        self.gui_cells = None

        self.init_game()

    def init_game(self):
        self.game = Minesweeper()
        self.header['text'] = 'Minesweeper'

        self.gui_cells = {}

        canvas_width = self.CELL_WIDTH * self.game.width
        canvas_height = self.CELL_HEIGHT * self.game.height

        self.canvas = Canvas(self.root, width=canvas_width, height=canvas_height)
        self.canvas.grid(row=1)

        self.draw_canvas()

    def draw_canvas(self):
        for cell in self.game.board:
            cell.object_id = self.canvas.create_rectangle(cell.x * self.CELL_WIDTH, cell.y * self.CELL_HEIGHT,
                                                          (cell.x + 1) * self.CELL_WIDTH,
                                                          (cell.y + 1) * self.CELL_HEIGHT,
                                                          fill="grey", outline="black")
            self.canvas.tag_bind(cell.object_id, sequence='<Button-1>', func=self.left_click_callback)
            self.canvas.tag_bind(cell.object_id, sequence='<Button-2>', func=self.right_click_callback)
            self.gui_cells[cell.object_id] = cell

    def left_click_callback(self, event):
        cell = self.gui_cells[event.widget.find_closest(event.x, event.y)[0]]
        print('Got left click on ', cell)
        res = self.game.reveal(cell.x, cell.y)
        if res:
            for object_id, cell in self.gui_cells.items():
                if cell.flagged:
                    self.canvas.itemconfigure(object_id, fill='orange')
                    continue
                elif not cell.revealed:
                    continue

                if cell.has_mine:
                    self.canvas.itemconfigure(object_id, fill='red')
                elif cell.adjacent_mines == 0:
                    self.canvas.itemconfigure(object_id, fill='white')
                else:
                    self.canvas.delete(object_id)
                    text_x = cell.x * self.CELL_WIDTH + self.CELL_WIDTH / 2
                    text_y = cell.y * self.CELL_HEIGHT + self.CELL_HEIGHT / 2
                    del self.gui_cells[cell.object_id]
                    cell.object_id = self.canvas.create_text((text_x, text_y),
                                                             text=str(cell.adjacent_mines),
                                                             fill=self.number_colors.get(cell.adjacent_mines, 'black'))
                    self.canvas.tag_bind(cell.object_id, sequence='<Button-1>', func=self.left_click_callback)
                    self.canvas.tag_bind(cell.object_id, sequence='<Button-2>', func=self.right_click_callback)
                    self.gui_cells[cell.object_id] = cell
            if self.game.is_won():
                self.header['text'] = 'You won!'
            elif self.game.is_lost():
                self.header['text'] = 'You lost!'

    def right_click_callback(self, event):
        cell = self.gui_cells[event.widget.find_closest(event.x, event.y)[0]]
        print('Got right click on ', cell)
        cell.flagged = not cell.flagged
        self.canvas.itemconfigure(cell.object_id, fill='orange' if cell.flagged else 'grey')


root = Tk()
gui = MinesweeperGui(root)
root.mainloop()
