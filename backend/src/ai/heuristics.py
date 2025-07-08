import os
import json
import logging
from typing import Dict, Any, List
from src.core.board import Board

logger = logging.getLogger(__name__)

# The default "Snake" gradient matrix encourages placing the largest tiles in the top-left corner,
# descending in a snake pattern down the board. This is mathematically optimal for 2048.
DEFAULT_GRADIENT_WEIGHTS = [
    65536.0, 32768.0, 16384.0, 8192.0,
    512.0,   1024.0,  2048.0,  4096.0,
    256.0,   128.0,   64.0,    32.0,
    2.0,     4.0,     8.0,     16.0
]

GRADIENT_WEIGHTS = list(DEFAULT_GRADIENT_WEIGHTS)
WEIGHT_GRADIENT = 1.0
WEIGHT_EMPTY = 270.0
WEIGHT_PENALTY = 11.0

def get_weights_path() -> str:
    # Resolve to backend/best_weights.json
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "best_weights.json")

def load_saved_weights() -> Dict[str, Any]:
    global GRADIENT_WEIGHTS, WEIGHT_GRADIENT, WEIGHT_EMPTY, WEIGHT_PENALTY
    path = get_weights_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            if "gradient_weights" in data:
                GRADIENT_WEIGHTS = [float(x) for x in data["gradient_weights"]]
            if "weight_gradient" in data:
                WEIGHT_GRADIENT = float(data["weight_gradient"])
            if "weight_empty" in data:
                WEIGHT_EMPTY = float(data["weight_empty"])
            if "weight_penalty" in data:
                WEIGHT_PENALTY = float(data["weight_penalty"])
            logger.info(f"Loaded evolved weights from {path} (Gen {data.get('generation', 0)}, Record Max Tile: {data.get('best_max_tile', 0)})")
            return data
        except Exception as e:
            logger.warning(f"Could not load saved weights from {path}: {e}")
    return {}

def save_weights(gradient_weights: List[float], weight_gradient: float, weight_empty: float, weight_penalty: float, meta: Dict[str, Any] = None) -> None:
    global GRADIENT_WEIGHTS, WEIGHT_GRADIENT, WEIGHT_EMPTY, WEIGHT_PENALTY
    GRADIENT_WEIGHTS = list(gradient_weights)
    WEIGHT_GRADIENT = float(weight_gradient)
    WEIGHT_EMPTY = float(weight_empty)
    WEIGHT_PENALTY = float(weight_penalty)
    
    path = get_weights_path()
    payload = {
        "gradient_weights": GRADIENT_WEIGHTS,
        "weight_gradient": WEIGHT_GRADIENT,
        "weight_empty": WEIGHT_EMPTY,
        "weight_penalty": WEIGHT_PENALTY
    }
    if meta:
        payload.update(meta)
        
    try:
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        logger.info(f"Saved evolved weights to {path}")
    except Exception as e:
        logger.error(f"Failed to save weights to {path}: {e}")

# Load weights upon startup if a trained model exists
load_saved_weights()

def evaluate_board(board: Board) -> float:
    """
    Evaluates the board state using a highly optimized Snake Gradient heuristic,
    empty cell bonuses, and clustering penalties.
    """
    grid = board.grid
    empty_cells = len(board.get_empty_cells())
    
    if empty_cells == 16:
        return 0.0

    score = 0.0
    penalty = 0.0
    
    for i in range(16):
        val = grid[i]
        if val > 0:
            # Add gradient score based on tile position
            score += val * GRADIENT_WEIGHTS[i] * WEIGHT_GRADIENT
            
            # Add clustering penalty for non-matching neighbors
            r, c = i // 4, i % 4
            if c < 3:
                right_val = grid[i + 1]
                if right_val > 0:
                    penalty += abs(val - right_val)
            if r < 3:
                down_val = grid[i + 4]
                if down_val > 0:
                    penalty += abs(val - down_val)

    score += empty_cells * WEIGHT_EMPTY
    score -= penalty * WEIGHT_PENALTY
    
    return score
