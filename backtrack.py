import copy


def backtrack(solutions, constrained_cells, candidate):
    if reject_candidate(constrained_cells, candidate):
        return
    if accept_candidate(constrained_cells, candidate):
        solutions.append(candidate)
    extension = generate_first_extension(candidate)
    while extension is not None:
        backtrack(solutions, constrained_cells, extension)
        extension = generate_next_extension(extension)


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


def accept_candidate(constrained_cells, candidate):
    return len(candidate) == len(constrained_cells)


def generate_first_extension(candidate):
    next_candidate = copy.copy(candidate)
    next_candidate.append(0)
    return next_candidate


def generate_next_extension(candidate):
    if candidate[-1] == 1:
        return None
    next_candidate = copy.copy(candidate)
    next_candidate[-1] = 1
    return next_candidate
