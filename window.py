#!/usr/bin/env python
import tkinter as tk

CELL_WIDTH = 16
CELL_HEIGHT = 16


def callback():
    print("click!")


class Application(tk.Frame):
    def __init__(self, master=None, rows=10, columns=10, mines=10):
        tk.Frame.__init__(self, master)
        self.master.title("Minesweeper")
        self.master.resizable(False, False)


        self.init_game(rows, columns, mines)

        self.master.lift()
        self.master.attributes('-topmost', True)
        self.master.after_idle(self.master.attributes, '-topmost', False)

        self.create_widgets()

    def init_game(self, rows=10, columns=10, mines=10):
        width = columns * CELL_WIDTH
        height = rows * CELL_HEIGHT
        self.master.geometry("{}x{}".format(width, height))
        self.grid(rowspan=rows, columnspan=columns, padx=9, pady=9)

    def create_widgets(self):
        for i in range(100):
            b = tk.Button(self.master, text="", command=callback)
            b.grid(column=int(i % 10), row=int(i / 10))


app = Application()
app.mainloop()
