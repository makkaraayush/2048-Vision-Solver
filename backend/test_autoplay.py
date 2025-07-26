import time
from src.vision.scanner import GameScanner
from src.core.controller import GameController
from src.ai.expectimax import ExpectimaxAI

def main():
    scanner = GameScanner()
    controller = GameController()
    ai = ExpectimaxAI(max_depth=3)
    print("Testing scanner + controller autoplay...")

if __name__ == '__main__':
    main()
