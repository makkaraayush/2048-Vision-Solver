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
DEFAULT_WEIGHT_GRADIENT = 1.0
DEFAULT_WEIGHT_EMPTY = 270.0
DEFAULT_WEIGHT_PENALTY = 11.0

# Current active parameters
GRADIENT_WEIGHTS = list(DEFAULT_GRADIENT_WEIGHTS)
WEIGHT_GRADIENT = DEFAULT_WEIGHT_GRADIENT
WEIGHT_EMPTY = DEFAULT_WEIGHT_EMPTY
WEIGHT_PENALTY = DEFAULT_WEIGHT_PENALTY

active_model_mode = "default"  # "default" or "champion"

def get_weights_path() -> str:
    # Resolve to backend/best_weights.json
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "best_weights.json")

def has_champion() -> bool:
    path = get_weights_path()
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return "gradient_weights" in data and len(data["gradient_weights"]) == 16
    except Exception:
        return False

def get_champion_meta() -> Dict[str, Any]:
    path = get_weights_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def apply_default_weights():
    global GRADIENT_WEIGHTS, WEIGHT_GRADIENT, WEIGHT_EMPTY, WEIGHT_PENALTY, active_model_mode
    GRADIENT_WEIGHTS = list(DEFAULT_GRADIENT_WEIGHTS)
    WEIGHT_GRADIENT = DEFAULT_WEIGHT_GRADIENT
    WEIGHT_EMPTY = DEFAULT_WEIGHT_EMPTY
    WEIGHT_PENALTY = DEFAULT_WEIGHT_PENALTY
    active_model_mode = "default"
    logger.info("Activated [Default Baseline] heuristic weights.")

def apply_champion_weights() -> bool:
    global GRADIENT_WEIGHTS, WEIGHT_GRADIENT, WEIGHT_EMPTY, WEIGHT_PENALTY, active_model_mode
    path = get_weights_path()
    if not os.path.exists(path):
        logger.warning("No champion weights found on disk. Falling back to Default.")
        apply_default_weights()
        return False
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
        active_model_mode = "champion"
        logger.info(f"Activated [Evolved Champion] weights (Gen {data.get('generation', 0)}, Record Tile: {data.get('best_max_tile', 0)})")
        return True
    except Exception as e:
        logger.error(f"Failed to load champion weights: {e}")
        apply_default_weights()
        return False

def set_active_model(mode: str) -> str:
    if mode == "champion" and has_champion():
        apply_champion_weights()
    else:
        apply_default_weights()
    return active_model_mode

def get_active_model_mode() -> str:
    return active_model_mode

def load_saved_weights() -> Dict[str, Any]:
    return get_champion_meta()

def save_weights(gradient_weights: List[float], weight_gradient: float, weight_empty: float, weight_penalty: float, meta: Dict[str, Any] = None) -> None:
    path = get_weights_path()
    payload = {
        "gradient_weights": [float(x) for x in gradient_weights],
        "weight_gradient": float(weight_gradient),
        "weight_empty": float(weight_empty),
        "weight_penalty": float(weight_penalty)
    }
    if meta:
        payload.update(meta)
        
    try:
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        logger.info(f"Saved evolved weights to {path}")
    except Exception as e:
        logger.error(f"Failed to save weights to {path}: {e}")

def delete_saved_weights() -> bool:
    """Deletes best_weights.json and resets active heuristics back to default baseline."""
    path = get_weights_path()
    deleted = False
    if os.path.exists(path):
        try:
            os.remove(path)
            deleted = True
            logger.info(f"Successfully deleted champion weights from {path}")
        except Exception as e:
            logger.error(f"Failed to delete {path}: {e}")
    apply_default_weights()
    return deleted

# Startup: keep default weights active initially unless champion exists
apply_default_weights()

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
