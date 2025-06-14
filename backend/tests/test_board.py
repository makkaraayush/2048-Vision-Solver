from src.core.board import Board, Move

def test_initial_board():
    b = Board()
    assert len(b.get_empty_cells()) == 16
    assert b.get_max_tile() == 0

def test_non_cascading_merge():
    grid = [0] * 16
    grid[0] = 4; grid[1] = 4; grid[2] = 4
    b = Board(tuple(grid))
    b2, score, changed = b.move(Move.LEFT)
    assert changed is True
    assert score == 8
    assert b2.grid[0] == 8
    assert b2.grid[1] == 4
    assert b2.grid[2] == 0
