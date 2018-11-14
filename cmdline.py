from minesweeper import Minesweeper


class CmdlineClient(Minesweeper):
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
    game = CmdlineClient(10, 10, 50)
    game.print_grid()
    while not game.is_lost() and not game.is_won():
        x = input('Choose an x\n> ')
        y = input('Choose an y\n> ')
        try:
            game.reveal(int(x), int(y))
        except TypeError:
            print("x and y must be integers")
