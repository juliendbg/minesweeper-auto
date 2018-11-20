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

SHOW_CONSTRAINED = True
CONSTRAINED_COLOR = '#FFFFCC'
WORKING_COLOR = '#FFFF00'


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
        self.pending_hit_count = 0
        self.is_done = False

        self.pending_mines = set()
        self.pending_reveals = set()

    def run(self):
        start_ts = floor(time() * 1000)
        # print("Time since last frame: {} ms".format(start_ts - self.end_ts))

        self.handle_new_games()

        if self.handle_wins():
            return

        changed = self.handle_pending_hits()

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

    def handle_new_games(self):
        if self.gui.game != self.game:
            if self.game:
                print('New game started!')
            self.game = self.gui.game
            self.board = self.gui.game.board
            self.is_done = False

        if self.gui.game.board != self.board:
            raise Exception('Board has changed during a game')

    def handle_wins(self):
        if self.game.is_won() or self.game.is_lost():
            if not self.is_done:
                print('pending: {}, backtracking: {}, random: {}'.format(
                    self.pending_hit_count, self.backtracking_count, self.random_hit_count))
                self.is_done = True
            self.root.after(1000, self.run)
            return True
        return False

    def handle_pending_hits(self):
        while self.pending_mines:
            cell = self.pending_mines.pop()
            if not cell.is_flagged():
                self.gui.flag(cell.x, cell.y)
                self.pending_hit_count += 1
                return True

        while self.pending_reveals:
            cell = self.pending_reveals.pop()
            if not cell.is_revealed():
                self.gui.reveal(cell.x, cell.y)
                self.pending_hit_count += 1
                return True

        return False

    def random_guess(self):
        playable = [_cell for _cell in self.board if _cell.is_playable()]
        shuffle(playable)
        cell = playable[0]
        print('Trying random guess: {}, {}'.format(cell.x, cell.y))
        self.gui.reveal(cell.x, cell.y)

    def flag_obvious_spots(self):
        board = [_cell for _cell in self.board if _cell.is_revealed() and _cell.status() != 0]
        shuffle(board)
        for cell in board:
            playable = [_cell for _cell in cell.get_surroundings() if _cell.is_playable()]
            flagged = [_cell for _cell in cell.get_surroundings() if _cell.is_flagged()]

            if cell.status() > len(flagged) and len(playable) == cell.status() - len(flagged):
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
                for _cell in playable:
                    self.gui.reveal(_cell.x, _cell.y)
                    return True
        return False

    @staticmethod
    def candidate_generator(constrained_cells, max_mines):
        for mine_count in range(0, max_mines):
            for candidate in itertools.combinations(constrained_cells, mine_count):
                yield list(candidate)

    @staticmethod
    def is_in_local_constraint(cell, local_constraint):
        for _cell in local_constraint:
            if set(cell.get_surroundings()).intersection(set(_cell.get_surroundings())):
                return True
        return False

    def resolve_constraints(self):
        local_constraint_groups = self.build_local_constraint_groups()

        if not local_constraint_groups:
            return False

        while local_constraint_groups:
            solutions = []
            candidate = []
            constrained = list(local_constraint_groups.pop())

            if SHOW_CONSTRAINED:
                self.show_constrained(constrained, WORKING_COLOR)

            backtrack(solutions, constrained, candidate)

            if solutions:
                for cell_index in range(len(constrained)):
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
                        self.pending_mines.add(unanimous_cell)
                    else:
                        self.pending_reveals.add(unanimous_cell)

            # Handle one hit
            changed = self.handle_pending_hits()
            if changed:
                return True

        return False

    def show_constrained(self, constrained, color=CONSTRAINED_COLOR):
        for cell in constrained:
            if self.gui.canvas.itemcget(cell.object_ids[0], 'fill') != color:
                cell.updated = True
                self.gui.canvas.itemconfigure(cell.object_ids[0], fill=color)
        self.gui.root.update()

    def build_local_constraint_groups(self):
        constrained = set(_cell for _cell in self.board if _cell.is_constrained())

        previous_constraints = getattr(self, 'previous_constraints', None)

        if previous_constraints == constrained:
            return None

        if SHOW_CONSTRAINED:
            self.show_constrained(constrained)

        local_constraint_groups = []
        while len(constrained) > 0:
            local_group = {constrained.pop()}
            for _cell in constrained:
                if self.is_in_local_constraint(_cell, local_group):
                    local_group.add(_cell)
            constrained = constrained.difference(local_group)
            local_constraint_groups.append(local_group)

        local_constraint_groups = sorted(local_constraint_groups, key=lambda x: len(x))

        return local_constraint_groups


if __name__ == '__main__':
    root = Tk()
    ai = MinesweeperAi(root)

    root.after(2000, ai.run)

    root.mainloop()
