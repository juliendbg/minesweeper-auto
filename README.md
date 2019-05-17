# minesweeper-auto

This program is a minesweeper engine and an automatic solver.

It has been inspired by the following article by Magnus Hoff on improving the minesweeper game: [Solving Minesweeper ... and making it better](https://magnushoff.com/minesweeper/).

The repository includes:

- a command-line interface (not very useful),
- a GUI in tkinter to play the classic version of the game,
- an AI interface that extends the GUI interface and plays by itself.

## Usage

### GUI

```
python gui.py
```

Different difficulty levels can be selected from the menu bar:

- Easy: 10x10, 10 mines
- Medium: 16x16, 40 mines
- Hard: 24x24, 99 mines
- Extreme: 75x50, 650 mines

Controls:

- Click on the title to restart,
- right-click a hidden cell to flag it,
- click on a revealed square to auto-reveal adjacent cells.


### AI interface

```
python ai.py
```

The automatic solver can:

- flag cells that are obviously mines,
- reveal cells that are obviously safe,
- use a backtracking algorithm to solve bigger sets of constraints on multiple cells,
- randomly reveal hidden cells.
