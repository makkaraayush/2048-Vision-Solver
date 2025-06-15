import time
from src.core.board import Board, Move

def run():
    b = Board().spawn_tile().spawn_tile()
    start = time.perf_counter()
    n = 20000
    for _ in range(n):
        for m in Move:
            b.move(m)
    dur = time.perf_counter() - start
    print(f"Moves/sec: {(n * 4) / dur:.0f}")

if __name__ == '__main__':
    run()
