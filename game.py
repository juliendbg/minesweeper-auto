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


class Game(object):
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
            return
        if self.is_lost():
            return
        cell = self.get_cell(x, y)
        if cell.revealed:
            return
        cell.revealed = True
        if cell.has_mine:
            self.print_grid()
            print('You lost!')
        else:
            self.auto_reveal_cells()
            if self.is_won():
                print('You won!')
            self.print_grid()

    def auto_reveal_cells(self):
        while any(cell.is_revealable() for cell in self.board):
            for cell in self.board:
                if cell.is_revealable():
                    cell.revealed = True

    def print_grid(self):
        grid = '+---' * self.width + '+\n'
        for index, cell in enumerate(self.board):
            if index != 0 and index % self.width == 0:
                grid += '|\n'
                grid += '+---' * self.width + '+\n'
            grid += '| {} '.format(cell.display())
        grid += '|\n'
        grid += '+---' * self.width + '+\n'
        print(grid)


if __name__ == '__main__':
    game = Game()
    game.print_grid()
    while not game.is_lost() and not game.is_won():
        x = input('Choose an x\n> ')
        y = input('Choose an y\n> ')
        try:
            game.reveal(int(x), int(y))
        except TypeError:
            print("x and y must be integers")
    exit(0)
