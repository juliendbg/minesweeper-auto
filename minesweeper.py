import random
from math import floor


class Cell(object):
    def __init__(self, game, x, y, revealed=False, has_mine=False, adjacent_mines=0):
        self.game = game
        self.revealed = revealed
        self.has_mine = has_mine
        self.adjacent_mines = adjacent_mines
        self.x = x
        self.y = y

    def is_revealable(self):
        if self.revealed:
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

    def display(self):
        if not self.revealed:
            return '#'
        if self.revealed:
            if self.has_mine:
                return 'x'
            else:
                return ' ' if self.adjacent_mines == 0 else str(self.adjacent_mines)


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
        if cell.revealed:
            return False
        cell.revealed = True
        if not cell.has_mine:
            self.auto_reveal_cells()
        return True

    def auto_reveal_cells(self):
        while any(cell.is_revealable() for cell in self.board):
            for cell in self.board:
                if cell.is_revealable():
                    cell.revealed = True
