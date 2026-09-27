# Empirical Testing Logs & Benchmark History

This directory documents empirical verification runs and hardware-in-the-loop autonomous testing of the **CodeD3mon-2048** system.

Each test run evaluates the computer vision scanner, real-time Expectimax decision engine, and physical OS automation playing on the live official [2048 web client](https://play2048.co) across full gameplay sessions.

---

## 📈 Benchmark Summary Table

| Run ID | Date | Configuration / Model | Max Tile | Score | Moves | Avg Latency | Video Log | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[Test #1](test_01_baseline_default/)** | 2026-09-27 | **Default Baseline Heuristics** (`DEFAULT_GRADIENT_WEIGHTS`) | **1024** | **12,120** | 708 | ~20 ms | [Timelapse](test_01_baseline_default/test_01_timelapse.mp4) | Completed |
| **Test #2** | Upcoming | **Evolved Champion Gen 50+** (`best_weights.json`) | *Target: 2048+* | *TBD* | *TBD* | ~22 ms | *Pending* | Scheduled |

---

## 🔬 Test Run Progression & Findings

### Test #1: Baseline Verification (Default Heuristics)
* **Goal**: Validate end-to-end vision perception, zero-hook tile classification (including yellow 128/256/512 disambiguation), browser CSS sync, and baseline Expectimax performance.
* **Result**: Flawless computer vision tracking with zero desyncs across 708 consecutive moves. Successfully assembled a **1024 tile** with a final score of **12,120**.
* **Key Finding**: In late-game crowded states ($\le 3$ free cells), the default gradient matrix required slightly stronger corner anchoring to avoid temporary monotonicity inversions. This provided the exact baseline targets for our in-memory evolutionary genetic trainer.
* **Full Report & Footage**: [View Test #1 Log](test_01_baseline_default/)
