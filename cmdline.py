from minesweeper import Minesweeper, Cell


class CmdlineClient(Minesweeper):
    @staticmethod
    def display_cell(cell):
        status = cell.status()
        if status == Cell.Status.FLAGGED:
            return 'o'
        if status == Cell.Status.HIDDEN:
            return '#'
        if status == Cell.Status.MINE:
            return 'x'
        else:
            return ' ' if status == 0 else str(status)

    def print_grid(self):
        grid = '+---' * self.width + '+\n'
        for index, cell in enumerate(self.board):
            if index != 0 and index % self.width == 0:
                grid += '|\n'
                grid += '+---' * self.width + '+\n'
            grid += '| {} '.format(self.display_cell(cell))
        grid += '|\n'
        grid += '+---' * self.width + '+\n'
        print(grid)

    def reveal(self, x, y):
        res = super(CmdlineClient, self).reveal(x, y)
        if res:
            self.print_grid()
            if self.is_won():
                print("You won!")
                exit(0)
            elif self.is_lost():
                print("You lost!")
                exit(0)


if __name__ == '__main__':
    game = CmdlineClient()
    game.print_grid()
    while not game.is_lost() and not game.is_won():
        x = input('Choose an x\n> ')
        y = input('Choose an y\n> ')
        try:
            game.reveal(int(x), int(y))
        except TypeError:
            print("x and y must be integers")
