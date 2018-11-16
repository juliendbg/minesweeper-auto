from random import randint
from tkinter import Tk

from gui import MinesweeperGui


class MinesweeperAi(object):
    def __init__(self, gui):
        self.root = gui.root
        self.gui = gui
        self.game = None
        self.board = None

    def run(self):
        self.game = self.gui.game
        self.board = self.gui.game.board

        if self.game.is_won() or self.game.is_lost():
            print('Stopping')
            self.root.after(10000, self.run)
            return

        changed = self.flag_obvious_spots()

        if not changed:
            changed = self.reveal_obvious_spots()

        if not changed:
            self.random_guess()

        self.root.after(100, self.run)

    def random_guess(self):
        x = randint(0, self.game.width - 1)
        y = randint(0, self.game.height - 1)
        print('Trying random guess: {}, {}'.format(x, y))
        self.gui.reveal(x, y)
        self.root.after(100, self.run)

    def flag_obvious_spots(self):
        print('Flagging obvious spots')
        for cell in [_cell for _cell in self.board if _cell.is_revealed() and _cell.status() != 0]:
            playable = [_cell for _cell in cell.get_surroundings() if _cell.is_playable()]
            flagged = [_cell for _cell in cell.get_surroundings() if _cell.is_flagged()]

            if cell.status() > len(flagged) and len(playable) == cell.status() - len(flagged):
                print('Working on cell: {} ({})'.format(cell, len(playable)))
                for _cell in playable:
                    self.gui.flag(_cell.x, _cell.y)
                    return True

        return False

    def reveal_obvious_spots(self):
        print('Revealing obvious spots')
        for cell in [_cell for _cell in self.board if _cell.is_revealed() and _cell.status() != 0]:
            playable = [_cell for _cell in cell.get_surroundings() if _cell.is_playable()]
            flagged = [_cell for _cell in cell.get_surroundings() if _cell.is_flagged()]

            if cell.status() == len(flagged):
                print('Working on cell: {} ({})'.format(cell, len(playable)))
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
