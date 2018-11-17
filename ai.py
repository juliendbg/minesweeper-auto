from math import floor
from random import shuffle
from time import time
from tkinter import Tk, Checkbutton, IntVar, NW, Frame, Label

from gui import MinesweeperGui


class MinesweeperAi(object):
    def __init__(self, master):
        self.root = master
        self.gui = MinesweeperGui(self.root)

        self.ai_frame = Frame(self.root)
        self.ai_frame.grid(row=0, rowspan=2, column=3, padx=10, pady=10)

        self.ai_status = Label(self.ai_frame, text='AI is initializing', width=12)
        self.ai_status.grid(row=0)
        self.auto_flag = IntVar(value=1)
        Checkbutton(self.ai_frame, text="Auto flag", variable=self.auto_flag).grid(row=1, sticky=NW)
        self.auto_reveal = IntVar(value=1)
        Checkbutton(self.ai_frame, text="Auto reveal", variable=self.auto_reveal).grid(row=2, sticky=NW)
        self.auto_constraints = IntVar(value=0)
        Checkbutton(self.ai_frame, text="Resolve constraints", variable=self.auto_constraints).grid(row=3, sticky=NW)
        self.random_reveal = IntVar(value=0)
        Checkbutton(self.ai_frame, text="Random reveal", variable=self.random_reveal).grid(row=4, sticky=NW)

        self.game = None
        self.board = None
        self.end_ts = floor(time() * 1000)

    def run(self):
        start_ts = floor(time() * 1000)
        # print("Time since last frame: {} ms".format(start_ts - self.end_ts))

        if self.gui.game != self.game:
            if self.game:
                print('Game has changed!')
            self.game = self.gui.game
            self.board = self.gui.game.board

        if self.gui.game.board != self.board:
            if self.board:
                print('Board has changed!')
            self.board = self.gui.game.board

        if self.game.is_won() or self.game.is_lost():
            self.root.after(1000, self.run)
            return

        changed = False

        if self.auto_flag.get() and not changed:
            changed = self.flag_obvious_spots()
            step = 'flag'

        if self.auto_reveal.get() and not changed:
            changed = self.reveal_obvious_spots()
            step = 'reveal'

        if self.auto_constraints.get() and not changed:
            changed = self.resolve_constraints()
            step = 'random'

        if self.random_reveal.get() and not changed:
            self.random_guess()
            step = 'random'

        self.end_ts = floor(time() * 1000)
        elapsed = self.end_ts - start_ts
        # print("Step '{}' frame time: {} ms".format(step, elapsed))

        if changed:
            self.ai_status['text'] = 'AI is working'
            next_in = max(10 - elapsed, 1)
        else:
            self.ai_status['text'] = 'AI is idle'
            next_in = max(100 - elapsed, 1)
        self.root.after(next_in, self.run)

    def random_guess(self):
        playable = [_cell for _cell in self.board if _cell.is_playable()]
        shuffle(playable)
        cell = playable[0]
        print('Trying random guess: {}, {}'.format(cell.x, cell.y))
        self.gui.reveal(cell.x, cell.y)

    def flag_obvious_spots(self):
        # print('Flagging obvious spots')
        board = [_cell for _cell in self.board if _cell.is_revealed() and _cell.status() != 0]
        shuffle(board)
        for cell in board:
            playable = [_cell for _cell in cell.get_surroundings() if _cell.is_playable()]
            flagged = [_cell for _cell in cell.get_surroundings() if _cell.is_flagged()]

            if cell.status() > len(flagged) and len(playable) == cell.status() - len(flagged):
                # print('Working on cell: {} ({})'.format(cell, len(playable)))
                for _cell in playable:
                    self.gui.flag(_cell.x, _cell.y)
                    return True

        return False

    def reveal_obvious_spots(self):
        # print('Revealing obvious spots')
        board = [_cell for _cell in self.board if _cell.is_revealed() and _cell.status() != 0]
        shuffle(board)
        for cell in board:
            playable = [_cell for _cell in cell.get_surroundings() if _cell.is_playable()]
            flagged = [_cell for _cell in cell.get_surroundings() if _cell.is_flagged()]

            if cell.status() == len(flagged):
                # print('Working on cell: {} ({})'.format(cell, len(playable)))
                for _cell in playable:
                    self.gui.reveal(_cell.x, _cell.y)
                    return True
        return False

    def resolve_constraints(self):
        return False


if __name__ == '__main__':
    root = Tk()
    ai = MinesweeperAi(root)

    root.after(2000, ai.run)

    root.mainloop()
