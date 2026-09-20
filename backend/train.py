import random
import time
import logging
import os
import sys
from typing import Tuple, List, Dict, Any, Optional, Callable

from src.core.board import Board, Move
from src.ai.expectimax import ExpectimaxSolver
import src.ai.heuristics as heur

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class Headless2048:
    """Fast in-memory headless 2048 game for simulation and training."""
    def __init__(self):
        self.board = Board()
        self.board = self.board.spawn_tile()
        self.board = self.board.spawn_tile()
        self.moves_made = 0
        self.total_score = 0
        
    def play_game(self, solver: ExpectimaxSolver) -> Tuple[int, int, int]:
        """
        Plays until game over.
        Returns: (max_tile, total_score, moves_made)
        """
        while not self.board.is_game_over():
            best_move, _ = solver.get_best_move(self.board)
            if best_move is None:
                break
                
            new_board, score_gained = self.board.move(best_move)
            if new_board is not None:
                self.board = new_board.spawn_tile()
                self.moves_made += 1
                self.total_score += score_gained
            else:
                # No valid move from this state
                break
                
        return max(self.board.grid), self.total_score, self.moves_made

def calculate_level(max_tile: int) -> int:
    """Returns AI mastery level based on max tile achieved."""
    if max_tile >= 4096:
        return 5
    elif max_tile >= 2048:
        return 4
    elif max_tile >= 1024:
        return 3
    elif max_tile >= 512:
        return 2
    else:
        return 1

class GeneticTrainer:
    """
    Continuous evolutionary trainer.
    Loads champion baseline from best_weights.json if available,
    tests mutations, and retrains continuously.
    """
    def __init__(self, callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.callback = callback
        self.stop_requested = False
        self.solver = ExpectimaxSolver(max_depth=3)
        
        # Load existing saved baseline if available
        saved = heur.load_saved_weights()
        if saved and "gradient_weights" in saved:
            self.champion_weights = list(saved["gradient_weights"])
            self.champion_gradient = float(saved.get("weight_gradient", 1.0))
            self.champion_empty = float(saved.get("weight_empty", 270.0))
            self.champion_penalty = float(saved.get("weight_penalty", 11.0))
            self.generation = int(saved.get("generation", 0))
            self.best_max_tile = int(saved.get("best_max_tile", 0))
            self.best_score = int(saved.get("best_score", 0))
            self.games_played = int(saved.get("games_played", 0))
            logger.info(f"Loaded existing champion: Gen {self.generation}, Record Tile: {self.best_max_tile}, Score: {self.best_score}")
        else:
            self.champion_weights = list(heur.DEFAULT_GRADIENT_WEIGHTS)
            self.champion_gradient = 1.0
            self.champion_empty = 270.0
            self.champion_penalty = 11.0
            self.generation = 0
            self.best_max_tile = 0
            self.best_score = 0
            self.games_played = 0

    def mutate(self) -> Tuple[List[float], float, float, float]:
        """Creates a mutated candidate from champion baseline."""
        new_weights = list(self.champion_weights)
        for i in range(len(new_weights)):
            if random.random() < 0.20:
                change = 1.0 + random.uniform(-0.15, 0.15)
                new_weights[i] = max(1.0, new_weights[i] * change)
                
        # Mutate empty weight and penalty weight occasionally
        empty_w = self.champion_empty
        if random.random() < 0.25:
            empty_w = max(50.0, empty_w * (1.0 + random.uniform(-0.10, 0.10)))
            
        penalty_w = self.champion_penalty
        if random.random() < 0.25:
            penalty_w = max(1.0, penalty_w * (1.0 + random.uniform(-0.10, 0.10)))
            
        return new_weights, self.champion_gradient, empty_w, penalty_w

    def evaluate_candidate(self, weights: List[float], grad_w: float, empty_w: float, penalty_w: float) -> Tuple[int, int, int]:
        """Temporarily sets heuristics weights and simulates a headless game."""
        heur.GRADIENT_WEIGHTS = weights
        heur.WEIGHT_GRADIENT = grad_w
        heur.WEIGHT_EMPTY = empty_w
        heur.WEIGHT_PENALTY = penalty_w
        
        game = Headless2048()
        return game.play_game(self.solver)

    def run(self):
        """Runs the evolutionary training loop until stop_requested."""
        self.stop_requested = False
        logger.info("🧠 Evolutionary Trainer Started. Evolving neural heuristics...")
        
        while not self.stop_requested:
            self.generation += 1
            is_mutation = (self.generation > 1 or self.best_max_tile > 0)
            
            if is_mutation:
                c_weights, c_grad, c_empty, c_penalty = self.mutate()
            else:
                c_weights, c_grad, c_empty, c_penalty = self.champion_weights, self.champion_gradient, self.champion_empty, self.champion_penalty

            status_msg = f"Evaluating Generation {self.generation}..."
            if self.callback:
                self.callback({
                    "generation": self.generation,
                    "level": calculate_level(self.best_max_tile),
                    "best_max_tile": self.best_max_tile,
                    "best_score": self.best_score,
                    "current_max_tile": 0,
                    "current_score": 0,
                    "games_played": self.games_played,
                    "status": status_msg
                })

            start_t = time.time()
            max_tile, score, moves = self.evaluate_candidate(c_weights, c_grad, c_empty, c_penalty)
            self.games_played += 1
            duration = time.time() - start_t
            
            # Candidate fitness formula: Heavily prioritize max tile, then total score
            candidate_fitness = (max_tile * 10) + score
            champion_fitness = (self.best_max_tile * 10) + self.best_score

            improved = False
            if candidate_fitness > champion_fitness or self.best_max_tile == 0:
                improved = True
                self.best_max_tile = max(self.best_max_tile, max_tile)
                self.best_score = max(self.best_score, score)
                self.champion_weights = list(c_weights)
                self.champion_empty = c_empty
                self.champion_penalty = c_penalty
                
                # Persist to disk so progress is never lost and live solver uses it!
                heur.save_weights(
                    self.champion_weights,
                    self.champion_gradient,
                    self.champion_empty,
                    self.champion_penalty,
                    meta={
                        "generation": self.generation,
                        "best_max_tile": self.best_max_tile,
                        "best_score": self.best_score,
                        "games_played": self.games_played
                    }
                )
                logger.info(f"🏆 NEW CHAMPION! Gen {self.generation}: Max Tile = {max_tile}, Score = {score} ({duration:.1f}s)")
                status_msg = f"🎉 New Champion! Tile {max_tile} (Score {score})"
            else:
                logger.info(f"Gen {self.generation} completed. Tile = {max_tile}, Score = {score}. Champion remains Tile {self.best_max_tile}.")
                status_msg = f"Gen {self.generation} ended: Tile {max_tile} (Score {score})"

            if self.callback:
                self.callback({
                    "generation": self.generation,
                    "level": calculate_level(self.best_max_tile),
                    "best_max_tile": self.best_max_tile,
                    "best_score": self.best_score,
                    "current_max_tile": max_tile,
                    "current_score": score,
                    "games_played": self.games_played,
                    "status": status_msg
                })
                
            time.sleep(0.05)

        logger.info("Evolutionary Trainer stopped.")

    def stop(self):
        self.stop_requested = True

def main():
    print("=========================================================")
    print("    CODED3MON-2048: EVOLUTIONARY HEURISTIC TRAINER      ")
    print("=========================================================")
    print("Simulating headless games. Retraining and evolving weights.")
    print("Champion models are automatically saved to best_weights.json.\n")
    
    trainer = GeneticTrainer()
    try:
        trainer.run()
    except KeyboardInterrupt:
        print("\nStopping training. Progress saved.")
        trainer.stop()

if __name__ == "__main__":
    main()
