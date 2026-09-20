import random
import time
import json
import os
from typing import Tuple, List, Optional
from src.core.board import Board, Move
from src.ai.heuristics import evaluate_board
from src.ai.expectimax import ExpectimaxAI

def get_mutation_rate(gen: int) -> float:
    return max(0.02, 0.15 * (0.95 ** gen))
