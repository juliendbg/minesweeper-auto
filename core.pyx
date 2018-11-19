def get_surroundings(int x, int y, game):
    coords = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
              (x - 1, y), (x + 1, y),
              (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)]
    cells = [get_cell(_x, _y, game)
             for _x, _y in coords
             if 0 <= _x < game.width and 0 <= _y < game.height]
    return cells

def get_cell(int x, int y, game):
    return game.board[y * game.width + x]
