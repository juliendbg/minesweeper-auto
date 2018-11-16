import random
from enum import Enum
from math import floor


class Cell(object):
    class Status(Enum):
        FLAGGED = 'F'
        HIDDEN = 'H'
        MINE = 'M'

    def __init__(self, game, x, y, has_mine=False, revealed=False):
        self.game = game
        self.x = x
        self.y = y
        self.has_mine = has_mine
        self.revealed = revealed
        self.flagged = False
        self.adjacent_mines = 0

    def __str__(self):
        return 'Cell({}, x={}, y={}, has_mine={}, revealed={}, flagged={})'.format(
            self.status(), self.x, self.y, self.has_mine, self.revealed, self.flagged)

    def is_revealed(self):
        return self.revealed

    def is_playable(self):
        return not self.revealed and not self.flagged

    def is_flagged(self):
        return self.flagged

    def is_revealable(self):
        if self.revealed or self.flagged:
            return False
        surroundings = self.get_surroundings()
        return any(cell.revealed and cell.adjacent_mines == 0 and not cell.has_mine for cell in surroundings)

    def get_surroundings(self):
        x = self.x
        y = self.y
        coords = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                  (x - 1, y), (x + 1, y),
                  (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)]
        cells = [self.game.get_cell(_x, _y)
                 for _x, _y in coords
                 if 0 <= _x < self.game.width and 0 <= _y < self.game.height]
        return cells

    def status(self):
        if self.flagged:
            return Cell.Status.FLAGGED
        if not self.revealed:
            return Cell.Status.HIDDEN
        else:
            if self.has_mine:
                return Cell.Status.MINE
            else:
                return self.adjacent_mines


class Minesweeper(object):
    def __init__(self, width=10, height=10, mine_count=10):
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.board = None
        self.init_board()

    def init_board(self):
        self.board = []
        remaining_mines = self.mine_count
        board_size = self.width * self.height
        for index in range(board_size):
            x = index % self.width
            y = floor(index / self.width)
            self.board.append(Cell(self, x, y))

        while remaining_mines:
            mine_index = random.randint(0, board_size - 1)
            while self.board[mine_index].has_mine:
                mine_index = random.randint(0, board_size)
            self.board[mine_index].has_mine = True
            remaining_mines -= 1

        for cell in self.board:
            cell.adjacent_mines = self.count_adjacent_mines(cell)

    def is_won(self):
        return not any(not cell.has_mine and not cell.revealed for cell in self.board)

    def is_lost(self):
        return any(cell.has_mine and cell.revealed for cell in self.board)

    def get_cell(self, x, y):
        return self.board[y * self.width + x]

    def count_adjacent_mines(self, cell):
        count = 0
        for _cell in cell.get_surroundings():
            if _cell.has_mine:
                count += 1
        return count

    def reveal(self, x, y):
        if self.is_won():
            return False
        if self.is_lost():
            return False
        cell = self.get_cell(x, y)
        if cell.flagged:
            return False
        if cell.revealed:
            return self.auto_reveal_if_completed(cell)
        cell.revealed = True
        if not cell.has_mine:
            self.auto_reveal_cells()
        return True

    def flag(self, x, y):
        if self.is_won():
            return False
        if self.is_lost():
            return False
        cell = self.get_cell(x, y)
        if cell.revealed:
            return False
        cell.flagged = not cell.flagged
        return True

    def auto_reveal_if_completed(self, cell):
        surroundings = cell.get_surroundings()
        flag_count = len([cell for cell in surroundings if cell.flagged])
        if not flag_count == cell.adjacent_mines:
            return False

        has_revealed = False
        unrevealed = [cell for cell in surroundings if not cell.revealed and not cell.flagged]
        for cell in unrevealed:
            cell.revealed = True
            if not cell.has_mine:
                self.auto_reveal_cells()
            has_revealed = True

        return has_revealed

    def auto_reveal_cells(self):
        while any(cell.is_revealable() for cell in self.board):
            for cell in self.board:
                if cell.is_revealable():
                    cell.revealed = True
