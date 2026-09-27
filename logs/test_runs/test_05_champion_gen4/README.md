# Test Run #5: 4096 Grandmaster Record & Tile Perception Analysis

- **Date**: September 28, 2026
- **Test Type**: Full-system live autonomous gameplay test (End-to-End Hardware-in-the-Loop)
- **Target Game**: Official 2048 Web Client (`play2048.co`)
- **Weights Used**: Evolved Champion Heuristics Generation 4 (`best_weights.json` — Level 5 Grandmaster)
- **Pre-Test Training**: 10 minutes of headless genetic evolutionary training (8 generations simulated, Gen 4 champion selected)
- **Hardware/Display Setup**: Dual Monitor 1080p (Game running on Monitor 1, CodeD3mon Telemetry Dashboard on Monitor 2)
- **Perception Mode**: Live OpenCV Zero-Hook Pixel Grab (`mss` + Blue-channel White Text Segmentation)

---

## Run Metrics & Results

| Metric | Measured Value | Notes |
| :--- | :--- | :--- |
| **Max Tile Reached** | **4096** 🌟 | **New System Record!** Assembled in corner position |
| **Final Game Score** | **44,688** | Active gameplay score when paused |
| **Total Moves Executed** | **~2,280+ moves** | Continuous high-throughput autonomous play |
| **Average Decision Latency** | **~24 ms / move** | Adaptive search depth 3–5 |
| **Search Tree Throughput** | **~49,500 nodes/sec** | Bitwise board representation + LRU caching |
| **Total Test Session Time** | **13 minutes 56 seconds** | Paused at 4096 milestone for perception analysis |
| **Session Outcome** | **Milestone Reached (Paused)** | Paused manually due to 4096 tile classification anomaly |

---

## Final Result & Score Screen

The session successfully created the **4096 tile**, reaching an active score of **44,688 points** before being paused:

![Test #5 Score Screen with 4096 Tile](test_05_final_score.png)

### Board State at 4096 Milestone:
```
┌──────┬──────┬──────┬──────┐
│ 4096 │   64 │   16 │    4 │
├──────┼──────┼──────┼──────┤
│   16 │    8 │    · │    2 │
├──────┼──────┼──────┼──────┤
│    4 │    4 │    · │    · │
├──────┼──────┼──────┼──────┤
│    2 │    · │    · │    2 │
└──────┴──────┴──────┴──────┘
```

---

## Video Recording & Timelapse

A condensed high-speed timelapse of the entire 13.9-minute autonomous session is stored alongside this report:

- **Full-Session Timelapse**: [`test_05_timelapse.mp4`](test_05_timelapse.mp4) (Dual-monitor view showing the live 2048 board on Monitor 1 achieving the 4096 tile and the CodeD3mon Telemetry Dashboard on Monitor 2).
- **Screenshot Artifact**: [`test_05_final_score.png`](test_05_final_score.png)

---

## Observations & Critical Bug Discovery: 4096 Tile Perception

### 1. Grandmaster 4096 Breakthrough
The Gen 4 Champion model demonstrated extraordinary tactical endurance, surpassing all previous runs by surviving 2,280+ moves and successfully combining two 2048 tiles into **4096**.

### 2. The 4096 Perception Anomaly (Classified as 64)
Upon synthesizing the 4096 tile in the top-left corner (`[0, 0]`), an optical perception anomaly occurred in the live computer vision pipeline:
- **Expected Recognition**: `4096`
- **Observed Recognition in Vision Matrix**: `64`
- **Impact**: Because the AI perceived its primary corner anchor as a low-value tile (`64`) instead of a permanent `4096` anchor, its directional value functions would have immediately prioritized moving away from the anchor. To preserve the game board and prevent incorrect moves, the gameplay session was intentionally paused.

### 3. Root Cause Investigation
In official `play2048.co`, tiles from `128` through `2048` utilize various shades of yellow/gold backgrounds. However, the **4096 tile** introduces a completely distinct visual scheme:
- A dark charcoal / blackish-brown background (`#3c3a32`, sampled BGR: `[62.8, 70.6, 80.1]`).
- White high-contrast text (`4096`).
- Because `4096` was absent from the static `tile_colors` palette in `scanner.py`, nearest-neighbor Euclidean distance mapped the dark brown tone to the nearest defined color, which happened to be `64` (`[59, 94, 246]`).
- This empirical finding provides the exact calibration values needed to add full native 4096 (and 8192) support to the perception engine.
