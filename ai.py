import itertools
from math import floor
from random import shuffle
from time import time
from tkinter import Tk, Checkbutton, IntVar, NW, Frame, Label

from backtrack import backtrack
from gui import MinesweeperGui

DEFAULT_AUTO_FLAG = 1
DEFAULT_AUTO_REVEAL = 1
DEFAULT_AUTO_CONSTRAINT = 0
DEFAULT_RANDOM_REVEAL = 0


class MinesweeperAi(object):
    def __init__(self, master):
        self.root = master
        self.gui = MinesweeperGui(self.root)

        self.ai_frame = Frame(self.root)
        self.ai_frame.grid(row=0, rowspan=2, column=3, padx=10, pady=10)

        self.ai_status = Label(self.ai_frame, text='AI is initializing', width=12)
        self.ai_status.grid(row=0)
        self.auto_flag = IntVar(value=DEFAULT_AUTO_FLAG)
        Checkbutton(self.ai_frame, text="Auto flag", variable=self.auto_flag).grid(row=1, sticky=NW)
        self.auto_reveal = IntVar(value=DEFAULT_AUTO_REVEAL)
        Checkbutton(self.ai_frame, text="Auto reveal", variable=self.auto_reveal).grid(row=2, sticky=NW)
        self.auto_constraints = IntVar(value=DEFAULT_AUTO_CONSTRAINT)
        Checkbutton(self.ai_frame, text="Resolve constraints", variable=self.auto_constraints).grid(row=3, sticky=NW)
        self.random_reveal = IntVar(value=DEFAULT_RANDOM_REVEAL)
        Checkbutton(self.ai_frame, text="Random reveal", variable=self.random_reveal).grid(row=4, sticky=NW)

        self.game = None
        self.board = None
        self.end_ts = floor(time() * 1000)
        self.backtracking_count = 0
        self.random_hit_count = 0
        self.is_done = False

    def run(self):
        start_ts = floor(time() * 1000)
        # print("Time since last frame: {} ms".format(start_ts - self.end_ts))

        if self.gui.game != self.game:
            if self.game:
                print('Game has changed!')
            self.game = self.gui.game
            self.board = self.gui.game.board
            self.is_done = False

        if self.gui.game.board != self.board:
            if self.board:
                print('Board has changed!')
            self.board = self.gui.game.board
            self.is_done = False

        if self.game.is_won() or self.game.is_lost():
            if not self.is_done:
                print('backtracking: {}, random: {}'.format(self.backtracking_count, self.random_hit_count))
                self.is_done = True
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
            if changed:
                self.backtracking_count += 1
            step = 'random'

        if self.random_reveal.get() and not changed:
            self.random_guess()
            self.random_hit_count += 1

            step = 'random'

        self.end_ts = floor(time() * 1000)
        elapsed = self.end_ts - start_ts
        # print("Step '{}' frame time: {} ms".format(step, elapsed))

        if changed:
            self.ai_status['text'] = 'AI is working'
            next_in = 10
        else:
            self.ai_status['text'] = 'AI is idle'
            next_in = 100
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

    @staticmethod
    def candidate_generator(constrained_cells, max_mines):
        for mine_count in range(0, max_mines):
            for candidate in itertools.combinations(constrained_cells, mine_count):
                yield list(candidate)

    def resolve_constraints(self):
        # print('Starting backtrack solving...')
        constrained = [_cell for _cell in self.board if _cell.is_constrained()]
        if not constrained:
            return False

        solutions = []  # array of sets of cells holding mines
        candidate = []

        backtrack(solutions, constrained, candidate)

        changed = False
        if solutions:
            # print('Found {} solutions'.format(len(solutions)))
            # print('Solutions: {}'.format(solutions))
            for cell_index in range(len(constrained) - 1):
                proposed_value = solutions[0][cell_index]
                is_unanimous = True
                for solution_index in range(1, len(solutions)):
                    if proposed_value != solutions[solution_index][cell_index]:
                        is_unanimous = False
                        break

                if not is_unanimous:
                    continue

                unanimous_cell = constrained[cell_index]
                unanimous_cell_is_mined = solutions[0][cell_index]
                if unanimous_cell_is_mined:
                    self.gui.flag(unanimous_cell.x, unanimous_cell.y)
                else:
                    self.gui.reveal(unanimous_cell.x, unanimous_cell.y)
                changed = True
                return True

        return changed


if __name__ == '__main__':
    root = Tk()
    ai = MinesweeperAi(root)

    root.after(2000, ai.run)

    root.mainloop()
