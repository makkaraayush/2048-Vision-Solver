import random
from enum import IntEnum
from typing import Tuple, List, Optional

BOARD_SIZE = 4
TOTAL_CELLS = 16

class Move(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
