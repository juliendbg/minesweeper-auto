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

    added_mines = {}
    played_cells = {}

    for index, is_mine in enumerate(candidate):
        cell = constrained_cells[index]
        for constraining_cell in cell.get_surroundings():
            if not constraining_cell.is_revealed():
                continue
            if is_mine and has_all_its_mines(constraining_cell, added_mines.get(constraining_cell, 0)):
                return True
            if not is_mine and needs_a_mine(constraining_cell,
                                            added_mines.get(constraining_cell, 0),
                                            played_cells.get(constraining_cell, 0)):
                return True

            added_mines[constraining_cell] = added_mines.get(constraining_cell, 0) + is_mine
            played_cells[constraining_cell] = played_cells.get(constraining_cell, 0) + 1

    return False


def has_all_its_mines(cell, added_mines=0):
    if not cell.is_revealed():
        raise Exception('Unable to check if hidden cell has all its mines')

    adjacent_mines = cell.status()
    current_flags = len([_cell for _cell in cell.get_surroundings() if _cell.is_flagged()])

    return current_flags + added_mines == adjacent_mines


def needs_a_mine(cell, added_mines=0, played_cells=0):
    if not cell.is_revealed():
        raise Exception('Unable to check if hidden cell has all its mines')

    adjacent_mines = cell.status()
    current_flags = len([_cell for _cell in cell.get_surroundings() if _cell.is_flagged()])

    hidden_cells = len([_cell for _cell in cell.get_surroundings() if _cell.is_playable()])

    missing_mines = adjacent_mines - current_flags - added_mines

    return missing_mines == hidden_cells - played_cells


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
