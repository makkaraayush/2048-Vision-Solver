import numpy as np
from enum import IntEnum
from typing import Tuple, List, Optional
import random

class Move(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class Board:
    """
    Core representation of the 2048 game board.
    Using a 1D tuple for immutability and fast hashing in LRU caches during AI evaluation.
    """
    
    __slots__ = ['grid', 'score']
    
    def __init__(self, grid: Optional[Tuple[int, ...]] = None, score: int = 0):
        # 4x4 grid flattened into a 16-element tuple
        self.grid = grid if grid is not None else tuple([0] * 16)
        self.score = score

    @staticmethod
    def _slide_and_merge_row(row: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int]:
        """Slides and merges a single row. Returns new row and gained score."""
        non_zero = [val for val in row if val != 0]
        merged = []
        score = 0
        skip = False
        
        for i in range(len(non_zero)):
            if skip:
                skip = False
                continue
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i+1]:
                merged.append(non_zero[i] * 2)
                score += non_zero[i] * 2
                skip = True
            else:
                merged.append(non_zero[i])
                
        # Pad with zeros
        while len(merged) < 4:
            merged.append(0)
            
        return tuple(merged), score

    def move(self, direction: Move) -> Tuple[Optional['Board'], int]:
        """
        Applies a move and returns the new board state and score gained.
        If the move is invalid (no tiles change), returns (None, 0).
        """
        new_grid = [0] * 16
        total_score = 0
        
        # Define index mappings for sliding in different directions
        if direction == Move.LEFT:
            indices = [[r*4 + c for c in range(4)] for r in range(4)]
        elif direction == Move.RIGHT:
            indices = [[r*4 + c for c in range(3, -1, -1)] for r in range(4)]
        elif direction == Move.UP:
            indices = [[r*4 + c for r in range(4)] for c in range(4)]
        elif direction == Move.DOWN:
            indices = [[r*4 + c for r in range(3, -1, -1)] for c in range(4)]
        else:
            raise ValueError("Invalid move direction")

        for row_indices in indices:
            row = tuple(self.grid[i] for i in row_indices)
            merged_row, score_gained = self._slide_and_merge_row(row)
            total_score += score_gained
            
            for i, val in zip(row_indices, merged_row):
                new_grid[i] = val
                
        new_grid_tuple = tuple(new_grid)
        if new_grid_tuple == self.grid:
            return None, 0
            
        return Board(grid=new_grid_tuple, score=self.score + total_score), total_score

    def get_empty_cells(self) -> List[int]:
        return [i for i, val in enumerate(self.grid) if val == 0]

    def is_game_over(self) -> bool:
        if 0 in self.grid:
            return False
        for d in Move:
            new_b, _ = self.move(d)
            if new_b is not None:
                return False
        return True

    def spawn_tile(self) -> 'Board':
        """Spawns a new tile (2 or 4) in a random empty spot. Used for simulation/testing."""
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return self
            
        idx = random.choice(empty_cells)
        val = 4 if random.random() < 0.1 else 2
        
        new_grid = list(self.grid)
        new_grid[idx] = val
        return Board(grid=tuple(new_grid), score=self.score)

    def print_board(self):
        for i in range(4):
            print(self.grid[i*4:(i+1)*4])
