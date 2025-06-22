from src.core.board import Board, Move

def test_board_creation():
    b = Board()
    assert len(b.get_empty_cells()) == 16
    assert b.get_max_tile() == 0

def test_moves():
    grid = (2, 2, 0, 0) + (0,) * 12
    b = Board(grid)
    nb, score, changed = b.move(Move.LEFT)
    assert changed is True
    assert score == 4
    assert nb.grid[0] == 4
