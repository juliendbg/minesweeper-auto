from tkinter import Menu, Label, Canvas, Tk

from minesweeper import Minesweeper, Cell


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

    def __init__(self, master):
        self.root = master

        self.root.title('Minesweeper')
        self.root.resizable(False, False)

        menubar = Menu(self.root)
        new_menu = Menu(menubar, tearoff=0)
        new_menu.add_command(label='Easy', command=lambda: self.init_game(10, 10, 10))
        new_menu.add_command(label='Medium', command=lambda: self.init_game(16, 16, 40))
        new_menu.add_command(label='Hard', command=lambda: self.init_game(24, 24, 99))
        new_menu.add_command(label='Extreme', command=lambda: self.init_game(75, 50, 650))
        menubar.add_cascade(label="New", menu=new_menu)
        self.root.config(menu=menubar)

        self.header = Label(self.root, text='', width=12)
        self.header.grid(row=0, column=1)
        self.header.bind('<Button-1>', lambda e: self.init_game())

        self.score = Label(self.root, text='', width=4)
        self.score.grid(row=0, column=0)

        self.game = None
        self.canvas = None

        self.init_game()

    def init_game(self, width=None, height=None, mine_count=None):
        if not width or not height or not mine_count:
            if self.game:
                width = self.game.width
                height = self.game.height
                mine_count = self.game.mine_count
            else:
                width = width or 24
                height = height or 24
                mine_count = mine_count or 99

        if self.canvas:
            self.canvas.grid_forget()
            self.canvas = None

        self.game = Minesweeper(width, height, mine_count)
        self.header['text'] = 'Minesweeper'
        self.score['text'] = self.game.mine_count

        canvas_width = self.CELL_WIDTH * self.game.width
        canvas_height = self.CELL_HEIGHT * self.game.height

        self.canvas = Canvas(self.root, width=canvas_width + self.PADDING, height=canvas_height + self.PADDING)
        self.canvas.grid(row=1, columnspan=2, padx=self.PADDING, pady=self.PADDING)

        self.draw_canvas()

    def draw_canvas(self):
        for cell in self.game.board:
            if cell.updated:
                self.draw_cell(cell)
                cell.updated = False

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

        if cell.status() == Cell.Status.FLAGGED:
            self.canvas.itemconfigure(cell.object_ids[0], fill=self.Colors.FLAGGED)
            return
        if cell.status() == Cell.Status.HIDDEN:
            self.canvas.itemconfigure(cell.object_ids[0], fill=self.Colors.HIDDEN)
            return

        if cell.status() == Cell.Status.MINE:
            self.canvas.itemconfigure(cell.object_ids[0], fill=self.Colors.MINE)
        elif cell.status() == 0:
            self.canvas.itemconfigure(cell.object_ids[0], fill=self.Colors.REVEALED)
        else:
            self.canvas.itemconfigure(cell.object_ids[0], fill=self.Colors.REVEALED)
            text_x = self.PADDING + cell.x * self.CELL_WIDTH + self.CELL_WIDTH / 2
            text_y = self.PADDING + cell.y * self.CELL_HEIGHT + self.CELL_HEIGHT / 2
            object_id = self.canvas.create_text((text_x, text_y),
                                                text=str(cell.adjacent_mines),
                                                fill=self.NUM_COLORS.get(cell.status(),
                                                                         self.NUM_COLORS['default']))
            self.canvas.tag_bind(object_id, sequence='<Button-1>', func=self.left_click_callback)
            self.canvas.tag_bind(object_id, sequence='<Button-2>', func=self.right_click_callback)
            cell.object_ids.append(object_id)

    def show_mines(self):
        for cell in self.game.board:
            if cell.has_mine:
                text_x = self.PADDING + cell.x * self.CELL_WIDTH + self.CELL_WIDTH / 2
                text_y = self.PADDING + cell.y * self.CELL_HEIGHT + self.CELL_HEIGHT / 2
                self.canvas.create_text((text_x, text_y), text='x', fill='black')

    def left_click_callback(self, event):
        object_id = event.widget.find_closest(event.x, event.y)[0]
        cell = self.get_cell(object_id)
        # print('Got left click on ', cell)
        self.reveal(cell.x, cell.y)

    def reveal(self, x, y):
        res = self.game.reveal(x, y)
        if res:
            self.draw_canvas()
            if self.game.is_won():
                self.header['text'] = 'You won!'
                self.score['text'] = '0'
            elif self.game.is_lost():
                self.header['text'] = 'You lost!'
                self.show_mines()
        return res

    def right_click_callback(self, event):
        object_id = event.widget.find_closest(event.x, event.y)[0]
        cell = self.get_cell(object_id)
        # print('Got right click on ', cell)
        self.flag(cell.x, cell.y)

    def flag(self, x, y):
        res = self.game.flag(x, y)
        if res:
            self.score['text'] = self.game.mine_count - len([cell for cell in self.game.board if cell.flagged])
            self.draw_cell(self.game.get_cell(x, y))

    def get_cell(self, object_id):
        for cell in self.game.board:
            if object_id in cell.object_ids:
                return cell
        raise Exception('{} not found in cells'.format(object_id))


if __name__ == '__main__':
    root = Tk()
    gui = MinesweeperGui(root)
    root.mainloop()
