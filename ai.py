from math import floor
from random import shuffle
from time import time
from tkinter import Tk

from gui import MinesweeperGui


class MinesweeperAi(object):
    def __init__(self, gui):
        self.root = gui.root
        self.gui = gui
        self.game = None
        self.board = None
        self.last_run = None

    def run(self):
        timestamp = floor(time() * 1000)
        if self.last_run:
            print('Frame time: {} ms'.format(timestamp - self.last_run))
        self.last_run = timestamp

        if self.gui.game != self.game:
            print('Game has changed!')
            self.game = self.gui.game

        if self.gui.game.board != self.board:
            print('Board has changed!')
            self.board = self.gui.game.board

        if self.game.is_won() or self.game.is_lost():
            self.root.after(1000, self.run)
            return

        changed = self.flag_obvious_spots()

        if not changed:
            changed = self.reveal_obvious_spots()

        if not changed:
            self.random_guess()

        self.root.after(100, self.run)

    def random_guess(self):
        playable = [_cell for _cell in self.board if _cell.is_playable()]
        shuffle(playable)
        cell = playable[0]
        print('Trying random guess: {}, {}'.format(cell.x, cell.y))
        self.gui.reveal(cell.x, cell.y)

    def flag_obvious_spots(self):
        # print('Flagging obvious spots')
        board = [_cell for _cell in self.board if _cell.is_revealed() and _cell.status() != 0]
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
        for cell in board:
            playable = [_cell for _cell in cell.get_surroundings() if _cell.is_playable()]
            flagged = [_cell for _cell in cell.get_surroundings() if _cell.is_flagged()]

            if cell.status() == len(flagged):
                # print('Working on cell: {} ({})'.format(cell, len(playable)))
                for _cell in playable:
                    self.gui.reveal(_cell.x, _cell.y)
                    return True
        return False


if __name__ == '__main__':
    root = Tk()
    gui = MinesweeperGui(root)
    ai = MinesweeperAi(gui)

    root.after(2000, ai.run)

    root.mainloop()