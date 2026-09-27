# Empirical Testing Logs & Benchmark History

This directory documents empirical verification runs and hardware-in-the-loop autonomous testing of the **CodeD3mon-2048** system.

Each test run evaluates the computer vision scanner, real-time Expectimax decision engine, and physical OS automation playing on the live official [2048 web client](https://play2048.co) across full gameplay sessions.

---

## Benchmark Summary Table

| Run ID | Date | Configuration / Model | Max Tile | Score | Moves | Avg Latency | Media Logs | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[Test #1](test_01_baseline_default/)** | 2026-09-27 | **Default Baseline Heuristics** (`DEFAULT_GRADIENT_WEIGHTS`) | **1024** | **12,120** | 708 | ~20 ms | [Timelapse](test_01_baseline_default/test_01_timelapse.mp4) • [Score Screen](test_01_baseline_default/test_01_final_score.png) | Completed |
| **[Test #2](test_02_baseline_default/)** | 2026-09-27 | **Default Baseline Heuristics** (`DEFAULT_GRADIENT_WEIGHTS`) | **1024** | **11,896** | 700 | ~20 ms | [Timelapse](test_02_baseline_default/test_02_timelapse.mp4) • [Score Screen](test_02_baseline_default/test_02_final_score.png) | Completed |
| **[Test #3](test_03_baseline_default/)** | 2026-09-27 | **Default Baseline Heuristics** (`DEFAULT_GRADIENT_WEIGHTS`) | **2048** 🏆 | **36,032** | 1,881 | ~25 ms | [Timelapse](test_03_baseline_default/test_03_timelapse.mp4) • [Score Screen](test_03_baseline_default/test_03_final_score.png) | **Victory Milestone** |

---

## Test Run Progression & Findings

### Test #1: Baseline Verification (Default Heuristics)
* **Goal**: Validate end-to-end vision perception, zero-hook tile classification (including yellow 128/256/512 disambiguation), browser CSS sync, and baseline Expectimax performance.
* **Result**: Flawless computer vision tracking with zero desyncs across 708 consecutive moves. Successfully assembled a **1024 tile** with a final score of **12,120**.
* **Key Finding**: In late-game crowded states ($\le 3$ free cells), the default gradient matrix required slightly stronger corner anchoring to avoid temporary monotonicity inversions. This provided the exact baseline targets for our in-memory evolutionary genetic trainer.
* **Full Report, Video & Screenshot**: [View Test #1 Log](test_01_baseline_default/)

### Test #2: Consistency & Reproducibility Run (Default Heuristics)
* **Goal**: Evaluate variance and stability across an independent full session under identical baseline weights.
* **Result**: High consistency with Test #1. Reached **1024 tile** in 700 moves with a final score of **11,896** points and zero perceptual faults.
* **Key Finding**: Confirms baseline heuristic determinism: the default gradient snake heuristic consistently and reliably solves boards up to 1024.
* **Full Report, Video & Screenshot**: [View Test #2 Log](test_02_baseline_default/)

### Test #3: 2048 Victory Milestone Run (Default Heuristics)
* **Goal**: Extended endurance test measuring late-game survival, deep branching under constrained board layouts, and 2048 completion.
* **Result**: **Unlocks 2048 Tile**! Concluded with **36,032 points** across **1,881 consecutive moves** in a 13.8-minute autonomous session.
* **Key Finding**: Successfully maintained descending snake monotonicity across Row 1 (`2048`, `1024`, `512`, `64`) and adapted Expectimax depth dynamically to 5 plys to resolve complex late-game collapses.
* **Full Report, Video & Screenshot**: [View Test #3 Log](test_03_baseline_default/)
