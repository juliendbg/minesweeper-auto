import copy
import itertools
from math import floor
from random import shuffle
from time import time
from tkinter import Tk, Checkbutton, IntVar, NW, Frame, Label

from gui import MinesweeperGui

DEFAULT_AUTO_FLAG = 0
DEFAULT_AUTO_REVEAL = 0
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
            self.ai_status['text'] = 'AI is resolving'
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

        self.backtrack(solutions, constrained, candidate)

        changed = False
        if solutions:
            print('Found {} solutions'.format(len(solutions)))
            print('Solutions: {}'.format(solutions))
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

    def backtrack(self, solutions, constrained_cells, candidate):
        # print('Next candidate is: {}'.format(candidate))
        if self.reject_candidate(constrained_cells, candidate):
            return
        if self.accept_candidate(constrained_cells, candidate):
            # print('Accepting candidate!')
            solutions.append(candidate)
        extension = self.generate_first_extension(candidate)
        while extension is not None:
            self.backtrack(solutions, constrained_cells, extension)
            extension = self.generate_next_extension(extension)

    @staticmethod
    def reject_candidate(constrained_cells, candidate):
        if len(candidate) > len(constrained_cells):
            return True

        new_mines = {}
        played_cells = {}
        for index, is_mine in enumerate(candidate):
            cell = constrained_cells[index]
            for constraining_cell in cell.get_surroundings():
                if not constraining_cell.is_revealed():
                    continue
                playable_cells = len([_cell for _cell in constraining_cell.get_surroundings() if _cell.is_playable()])
                played_cells[constraining_cell] = played_cells.get(constraining_cell, 0) + 1
                found_mines = len([_cell for _cell in constraining_cell.get_surroundings() if cell.is_flagged()])
                missing_mines = constraining_cell.status() - found_mines
                if missing_mines < 0:
                    return True
                new_mines[constraining_cell] = new_mines.get(constraining_cell, 0) + is_mine
                if new_mines[constraining_cell] > missing_mines:
                    return True
                if played_cells[constraining_cell] == playable_cells and new_mines[constraining_cell] < missing_mines:
                    return True
        return False

    @staticmethod
    def accept_candidate(constrained_cells, candidate):
        return len(candidate) == len(constrained_cells)

    @staticmethod
    def generate_first_extension(candidate):
        next_candidate = copy.copy(candidate)
        next_candidate.append(0)
        return next_candidate

    @staticmethod
    def generate_next_extension(candidate):
        if candidate[-1] == 1:
            return None
        next_candidate = copy.copy(candidate)
        next_candidate[-1] = 1
        return next_candidate


if __name__ == '__main__':
    root = Tk()
    ai = MinesweeperAi(root)

    root.after(2000, ai.run)

    root.mainloop()
