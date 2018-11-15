from tkinter import *

from minesweeper import Minesweeper

CELL_WIDTH = 16
CELL_HEIGHT = 16

game = Minesweeper()

canvas_width = CELL_WIDTH * game.width
canvas_height = CELL_HEIGHT * game.height

master = Tk()

header = Label(master, text="Minesweeper")
header.grid(row=0)
canvas = Canvas(master, width=canvas_width, height=canvas_height)
canvas.grid(row=1)

gui_cells = {}

number_colors = {
    1: 'blue',
    2: 'green',
    3: 'red'
}


def left_click_callback(event):
    cell = gui_cells[event.widget.find_closest(event.x, event.y)[0]]
    print('Got left click on ', cell)
    res = game.reveal(cell.x, cell.y)
    if res:
        for object_id, cell in gui_cells.items():
            if cell.flagged:
                canvas.itemconfigure(object_id, fill='orange')
                continue
            elif not cell.revealed:
                continue

            if cell.has_mine:
                canvas.itemconfigure(object_id, fill='red')
            elif cell.adjacent_mines == 0:
                canvas.itemconfigure(object_id, fill='white')
            else:
                canvas.delete(object_id)
                text_x = cell.x * CELL_WIDTH + CELL_WIDTH / 2
                text_y = cell.y * CELL_HEIGHT + CELL_HEIGHT / 2
                del gui_cells[cell.object_id]
                cell.object_id = canvas.create_text((text_x, text_y),
                                                    text=str(cell.adjacent_mines),
                                                    fill=number_colors.get(cell.adjacent_mines, 'black'))
                canvas.tag_bind(cell.object_id, sequence='<Button-1>', func=left_click_callback)
                canvas.tag_bind(cell.object_id, sequence='<Button-2>', func=right_click_callback)
                gui_cells[cell.object_id] = cell
        if game.is_won():
            header['text'] = 'You won!'
        elif game.is_lost():
            header['text'] = 'You lost!'


def right_click_callback(event):
    cell = gui_cells[event.widget.find_closest(event.x, event.y)[0]]
    print('Got right click on ', cell)
    cell.flagged = not cell.flagged
    canvas.itemconfigure(cell.object_id, fill='orange' if cell.flagged else 'grey')


for cell in game.board:
    cell.object_id = canvas.create_rectangle(cell.x * CELL_WIDTH, cell.y * CELL_HEIGHT,
                                             (cell.x + 1) * CELL_WIDTH, (cell.y + 1) * CELL_HEIGHT,
                                             fill="grey", outline="black")
    canvas.tag_bind(cell.object_id, sequence='<Button-1>', func=left_click_callback)
    canvas.tag_bind(cell.object_id, sequence='<Button-2>', func=right_click_callback)
    gui_cells[cell.object_id] = cell

mainloop()
