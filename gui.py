from tkinter import *

from minesweeper import Minesweeper


class MinesweeperGui(object):
    CELL_WIDTH = 16
    CELL_HEIGHT = 16
    PADDING = 5

    NUM_COLORS = {
        1: 'blue',
        2: 'green',
        3: 'red',
        4: 'dark blue',
        5: 'brown',
        6: 'cyan',
        7: 'black',
        8: 'grey',
        'default': 'black'
    }

    class Colors(object):
        REVEALED = 'white'
        FLAGGED = 'orange'
        HIDDEN = 'grey'
        MINE = 'red'
        OUTLINE = 'black'

    def __init__(self, root):
        self.root = root
        root.title('Minesweeper')
        root.resizable(False, False)

        self.header = Label(self.root, text='')
        self.header.grid(row=0)
        self.header.bind('<Button-1>', lambda e: self.init_game())

        self.game = None
        self.canvas = None

        self.init_game()

    def init_game(self):
        self.game = Minesweeper()
        self.header['text'] = 'Minesweeper'

        canvas_width = self.CELL_WIDTH * self.game.width
        canvas_height = self.CELL_HEIGHT * self.game.height

        self.canvas = Canvas(self.root, width=canvas_width + self.PADDING, height=canvas_height + self.PADDING)
        self.canvas.grid(row=1, padx=self.PADDING, pady=self.PADDING)

        self.draw_canvas()

    def draw_canvas(self):
        for cell in self.game.board:
            self.draw_cell(cell)

    def draw_cell(self, cell):
        if not hasattr(cell, 'object_ids'):
            object_id = self.canvas.create_rectangle(self.PADDING + cell.x * self.CELL_WIDTH,
                                                     self.PADDING + cell.y * self.CELL_HEIGHT,
                                                     self.PADDING + (cell.x + 1) * self.CELL_WIDTH,
                                                     self.PADDING + (cell.y + 1) * self.CELL_HEIGHT,
                                                     fill=self.Colors.HIDDEN, outline=self.Colors.OUTLINE)
            self.canvas.tag_bind(object_id, sequence='<Button-1>', func=self.left_click_callback)
            self.canvas.tag_bind(object_id, sequence='<Button-2>', func=self.right_click_callback)
            cell.object_ids = [object_id]

        if cell.flagged:
            self.canvas.itemconfigure(cell.object_ids[0], fill=self.Colors.FLAGGED)
            return
        if not cell.revealed:
            self.canvas.itemconfigure(cell.object_ids[0], fill=self.Colors.HIDDEN)
            return

        if cell.has_mine:
            self.canvas.itemconfigure(cell.object_ids[0], fill=self.Colors.MINE)
        elif cell.adjacent_mines == 0:
            self.canvas.itemconfigure(cell.object_ids[0], fill=self.Colors.REVEALED)
        else:
            self.canvas.itemconfigure(cell.object_ids[0], fill=self.Colors.REVEALED)
            text_x = self.PADDING + cell.x * self.CELL_WIDTH + self.CELL_WIDTH / 2
            text_y = self.PADDING + cell.y * self.CELL_HEIGHT + self.CELL_HEIGHT / 2
            object_id = self.canvas.create_text((text_x, text_y),
                                                text=str(cell.adjacent_mines),
                                                fill=self.NUM_COLORS.get(cell.adjacent_mines,
                                                                         self.NUM_COLORS['default']))
            self.canvas.tag_bind(object_id, sequence='<Button-1>', func=self.left_click_callback)
            self.canvas.tag_bind(object_id, sequence='<Button-2>', func=self.right_click_callback)
            cell.object_ids.append(object_id)

    def left_click_callback(self, event):
        object_id = event.widget.find_closest(event.x, event.y)[0]
        cell = self.get_cell(object_id)
        # print('Got left click on ', cell)
        res = self.game.reveal(cell.x, cell.y)
        if res:
            for cell in self.game.board:
                self.draw_cell(cell)
            if self.game.is_won():
                self.header['text'] = 'You won!'
            elif self.game.is_lost():
                self.header['text'] = 'You lost!'

    def right_click_callback(self, event):
        object_id = event.widget.find_closest(event.x, event.y)[0]
        cell = self.get_cell(object_id)
        # print('Got right click on ', cell)
        res = self.game.flag(cell.x, cell.y)
        if res:
            self.draw_cell(cell)

    def get_cell(self, object_id):
        for cell in self.game.board:
            if object_id in cell.object_ids:
                return cell
        raise Exception('{} not found in cells'.format(object_id))


root = Tk()
gui = MinesweeperGui(root)
root.mainloop()
