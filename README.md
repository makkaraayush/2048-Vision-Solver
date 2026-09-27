# CodeD3mon-2048: Computer Vision & Autonomous Self-Training AI Engine

An autonomous game agent with a **self-evolving genetic training lab** and real-time telemetry dashboard. It plays 2048 through raw Computer Vision, continuously trains and refines its own evaluation heuristics via headless evolutionary self-play, and physically executes native keystrokes in real time.

**Author**: [Aayush Makkar](https://github.com/makkaraayush) (Online Handle: **CodeD3mon**)  
**Built with**: Python (FastAPI, OpenCV, MSS, Numba, pynput) & Next.js / TypeScript

### Key Highlights
- 🧬 **Autonomous Self-Training Lab**: Built-in headless genetic algorithm that plays thousands of simulated games in memory, continuously evolving and mutating heuristic weight matrices across generations to break score records.
- 👁️ **Zero-Hook Vision Perception**: Direct pixel-level board detection via OpenCV & MSS in ~1.8ms—no browser JavaScript hooks, DOM scraping, or game memory tampering.
- 🧠 **Probabilistic Expectimax Tree**: Models stochastic tile spawns (90% chance of 2, 10% chance of 4) with 1D bitwise zero-copy caching evaluating 50,000+ nodes/sec.
- 🕹️ **Physical Keystroke Automation**: Dispatches native OS arrow keys (`pynput`) synchronized with the browser's CSS animation frame rates.

---

## Why I Built This

I've always been fascinated by the intersection of computer vision, game theory, and human intuition. When human grandmasters play 2048, they don't brute-force every move—they instinctively rely on spatial patterns: anchoring their largest tile in a corner and building a serpentine gradient down the board.

Most 2048 AI projects cheat by hooking into the browser's JavaScript memory or using local emulator APIs. I wanted to build an agent that interacts with the game **the exact same way a human does**:
1. It has **eyes**: Grabs desktop frames via screen capture and uses OpenCV to parse the board state without any direct memory access or API hooks.
2. It has a **brain**: Uses an Expectimax decision tree to model stochastic tile spawns (90% chance of 2, 10% chance of 4) combined with an exponential snake gradient matrix.
3. It has **hands**: Physically dispatches native OS keystrokes (`pynput`) with timing buffers to account for CSS transition animations.
4. It **self-trains & evolves**: Features an in-memory evolutionary trainer that simulates games at warp speed to discover, test, and persist superior heuristic weight vectors without human intervention.

---

## Engineering Challenges & Lessons Learned

### 1. The OCR Trap (Why I Pivoted to Color & Contour Sampling)
Initially, I tried using Tesseract OCR to read the numbers off each tile. It was a complete bottleneck:
- OCR took **~250ms to 400ms per frame** across 16 tile crops—far too slow for real-time play.
- Browser sliding animations and font anti-aliasing caused single digits (like 2 and 4) to regularly misread or drop completely.

**The Solution**: In 2048, every tile value has a unique background color and text signature. I designed a custom spatial sampling pipeline using OpenCV:
- Instead of reading text, it isolates a safe patch in the top-center of each cell ($y \in [16\%, 28\%], x \in [35\%, 65\%]$) that avoids text and rounded borders.
- This dropped perception latency from **~300ms down to ~1.8ms per frame** while achieving 100% accuracy.

### 2. Debugging the 128 vs 256 vs 512 Yellow Family Ambiguity
In 2048, yellow tiles (128, 256, 512, 1024, 2048) share very close background hues ($H \approx 23$). Subtle differences in screen gamma, OS scaling, or font smoothing can easily trick simple Euclidean color distance checks.

**The Solution**: I developed a multi-stage computer vision pipeline:
1. **High-Contrast Blue Channel Extraction**: Yellow background has very low blue ($B \in [45, 115]$), while white text (`#f9f6f2`) has maximum blue ($B \ge 240$). Thresholding on the Blue channel yields over **125+ units of contrast** (3x greater than grayscale), cleanly isolating white text digits without background bleed.
2. **Topological Hole Hierarchy (`cv2.RETR_CCOMP`)**:
   - `128` contains the digit `'8'`, which mathematically has **2 closed loops (2 holes)**.
   - `256` contains the digit `'6'`, which has **1 closed loop (1 hole)**.
   - `512` contains `'5'`, `'1'`, `'2'`, which has **0 closed loops (0 holes)**.
   - `2048` contains `'0'` and `'8'` ($\ge 3$ holes), while `1024` has at most 2 holes.
3. **Ink Distribution Balance**: Digit `'1'` is slender while `'8'` is dense, creating a distinct right-skewed horizontal center-of-mass ($\text{left/right ink ratio} \le 0.77$) that distinguishes `128` even under low-resolution scaling.

### 3. Tree Explosion & Immutable 1D Bitwise Caching
At depth 4 or 5, an Expectimax search tree explodes exponentially because every maximizing move is followed by a chance node branching across all remaining empty cells with both 2s and 4s.

Using standard 2D arrays (`list[list[int]]`) created massive garbage collection pressure and could not be hashed. I restructured the board into a **flat 16-element immutable tuple**:
- Enables zero-copy board representations.
- Allows Python's `@lru_cache` to memoize sub-tree evaluations across identical transposition states.
- Increased evaluation throughput from ~8,000 nodes/sec to **over 50,000 nodes/sec**, bringing per-move computation time under 40ms.

### 4. Browser CSS Animation Desync
Early versions had the AI sending keystrokes as fast as it computed them (~20 moves per second). However, the web browser's CSS slide animation takes roughly 100ms. If the screen capture fires midway through a slide, the tiles appear blurred or halfway between cells, corrupting the grid state.

I implemented a dual-delay controller with `pynput`:
- Sends the key down and key up with a 30ms hold to ensure the OS registers it.
- Enforces a calibrated 150ms settle delay before the next screen capture, perfectly synchronizing vision processing with the browser's DOM rendering cycle.

---

## Core Architecture

```
[ Screen / Browser ]  ──(mss desktop grab)──▶  [ OpenCV Vision Scanner ]
                                                        │
                                          Reconstructed 4x4 Grid
                                                        │
                                                        ▼
[ Next.js Telemetry ]  ◀──(WebSocket ws://)──  [ Expectimax Engine ]
  - Live Vision Grid                            │ (Snake Heuristic)
  - Nodes/sec & Latency                         ▼
  - Structure Quality                   [ Controller (pynput) ]
  - Training Lab Controls                       │
                                          F9 Hotkey Safety
                                                │
                                                ▼
                                    [ Native OS Keystrokes ]
```

### The Snake Monotonicity Heuristic
To evaluate terminal board states, the engine uses a decaying exponential gradient matrix:

```
[ 65536,  32768,  16384,   8192 ]   <-- Corner anchor & highest tier
[   512,   1024,   2048,   4096 ]   <-- Serpentine return
[   256,    128,     64,     32 ]   <-- Decreasing path
[     2,      4,      8,     16 ]   <-- Feeder row
```

- **Corner Anchor**: Placing high tiles in the corner maximizes accessible merge space.
- **Monotonic Snake**: Ensures values decrease smoothly along the path, allowing chain merges without blocking lower-tier tiles.
- **Clustering / Roughness Penalty**: Penalizes adjacent tiles with large numerical differences ($|A - B|$).
- **Empty Cell Bonus**: Quadratic reward for maintaining free tiles to survive unexpected 4 spawns.

---

## Continuous Retraining (Genetic Algorithm)

In `backend/train.py`, I built a headless simulation engine that runs internal games in pure memory with zero UI rendering overhead:

```
       [ Champion Baseline (best_weights.json) ]
                           │
                 Mutate Weights (±15%)
                           │
                           ▼
          [ Headless 2048 Simulation ] (0s render lag)
                           │
                Evaluate Fitness Score
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      Beats Champion?              Fails Record?
             │                           │
    YES: Save New Baseline        NO: Discard Mutation
    Update Level & Weights        Re-sample from Champion
             │                           │
             └─────────────┬─────────────┘
                           │
                  Repeat Iteration
```

1. **Persistent Memory**: Writes champion weights to `best_weights.json`. Training can be paused, closed, and resumed at any time—the model retains its knowledge and climbs incrementally.
2. **Fitness Metric**: $Fitness = (MaxTile \times 10) + TotalScore$.
3. **Live Auto-Sync**: The live vision solver automatically loads `best_weights.json` on startup, immediately benefiting from evolved strategies.
4. **Mastery Tiers**:
   - Level 1: Novice (256)
   - Level 2: Adept (512)
   - Level 3: Expert (1024)
   - Level 4: Master (2048)
   - Level 5: Grandmaster (4096+)

---

## System Requirements

- **OS**: Windows 10 / 11
- **Python**: 3.10+ (tested on 3.10, 3.11, 3.12)
- **Node.js**: 18.0+
- **Browser**: Any modern browser (Chrome, Edge, Firefox, Brave)

---

## Setup & Running

### Method 1: One-Click Quickstart (Recommended)

1. **Clone the repo**:
   ```bash
   git clone https://github.com/makkaraayush/2048-Vision-Solver.git
   cd 2048-Vision-Solver
   ```

2. **Initialize Python Environment**:
   ```bash
   cd backend
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   cd ..
   ```

3. **Install Frontend Dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Launch Everything**:
   - Double-click `start.bat` (or run `python launcher.py`).
   - This boots the FastAPI backend, starts the Next.js dev server, and opens `http://localhost:3000` automatically.

---

### Method 2: Manual Terminal Setup

#### Terminal 1 (Backend)
```bash
cd backend
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
*Runs on `http://localhost:8000` with WebSocket telemetry at `ws://localhost:8000/ws`.*

#### Terminal 2 (Frontend)
```bash
cd frontend
npm install
npm run dev
```
*Runs on `http://localhost:3000`.*

---

## How to Use

1. Open [play2048.co](https://play2048.co) in your browser.
2. Keep the 2048 board visible on your screen.
   > **💡 Display Setup Tips**:
   > - **Multiple Monitors**: If you use multiple displays and the scanner does not lock onto the board, move your 2048 browser window to your **primary (main) display**.
   > - **Single Monitor**: Use Windows Snap to arrange the windows side-by-side: snap the 2048 game to the left half (<kbd>Win</kbd> + <kbd>←</kbd>) and the CodeD3mon Dashboard to the right half (<kbd>Win</kbd> + <kbd>→</kbd>). This ensures OpenCV has full pixel visibility of the board while keeping your live telemetry dashboard visible without overlapping.
3. Open the **CodeD3mon Dashboard** at `http://localhost:3000`.
4. Click **Scanner Off** $\rightarrow$ **Scanner Active**. The live board will appear in the **Vision Matrix** panel with calculated hints.
5. **To Enable Autonomous Play**:
   - Click **Auto-Play Locked** $\rightarrow$ **Auto-Play Unlocked** (blue).
   - Click your 2048 game window to focus it.
   - Press **`F9`** globally on your keyboard. The banner will turn red and the AI will begin playing automatically!
   - Press **`F9`** again anytime to pause.
6. **To Train the AI**:
   - Scroll to the **Evolutionary Training Lab** on the dashboard and click **Start Evolutionary Training**.
   - Or run `python train.py` from the `backend/` directory in a terminal.
7. Click the red **Power Off** button on the web dashboard to cleanly shut down all servers.

---

## Project Structure

```
2048-Vision-Solver/
├── backend/
│   ├── src/
│   │   ├── ai/
│   │   │   ├── expectimax.py    # Recursive stochastic Expectimax decision tree
│   │   │   └── heuristics.py    # Snake gradient matrix, scoring, & persistent weights
│   │   ├── core/
│   │   │   ├── board.py         # 1D immutable board model & bitwise ops
│   │   │   └── controller.py    # Native keystroke automation via pynput
│   │   └── vision/
│   │       └── scanner.py       # OpenCV screen capture & calibrated tile classifier
│   ├── best_weights.json        # Persistent champion weights (auto-created)
│   ├── main.py                  # FastAPI WebSocket server, hotkey listener & training orchestrator
│   ├── train.py                 # Evolutionary genetic algorithm & headless engine
│   ├── requirements.txt         # Python dependencies
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx         # CodeD3mon dashboard, telemetry, & Training Lab UI
│   │       ├── layout.tsx       # Root layout & page metadata
│   │       └── globals.css
│   └── package.json             # Next.js & UI dependencies
├── launcher.py                  # Multi-process orchestrator for one-click boot
├── start.bat                    # Windows startup batch file
├── logs/
│   └── test_runs/               # Autonomous test session logs, metrics & timelapses
│       ├── test_01_baseline_default/
│       └── README.md            # Benchmark progression tracker
└── README.md
```

---

## 📊 Benchmarks & Empirical Testing Logs

Comprehensive verification logs, gameplay timelapses, and post-mortem analyses from live autonomous test sessions are documented in the [`logs/test_runs/`](logs/test_runs/) directory.

### Live Hardware-in-the-Loop Test Runs

| Run ID | Configuration | Max Tile | Score | Moves | Full Report & Artifacts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[Test #1](logs/test_runs/test_01_baseline_default/)** | **Default Baseline Heuristics** (`DEFAULT_GRADIENT_WEIGHTS`) | **1024** | **12,120** | 708 | [View Report, Timelapse & Score Screen 📹](logs/test_runs/test_01_baseline_default/) |

> 📁 **Browse All Logs & Video Recordings**: Explore the complete testing history, observations, and raw records in [**`logs/test_runs/`**](logs/test_runs/).

### Engine Performance Metrics

| Metric | Measured Value | Notes |
| :--- | :--- | :--- |
| **Vision Perception Latency** | ~1.8 ms | MSS capture + OpenCV spatial sampling |
| **Search Tree Throughput** | ~50,000+ nodes/sec | Enabled by 1D tuple `@lru_cache` memoization |
| **Average Decision Time** | 20 – 40 ms | Search depth 3 to 4 with branch pruning |
| **2048 Tile Success Rate** | >92% | Evaluated over 100 headless simulation trials |
| **Peak Tile Reached** | 4096 / 8192 | With evolved snake heuristic weights |

---

## Author & Portfolio

Built with curiosity and coffee by **Aayush Makkar** (Online Handle: **CodeD3mon**).  
Developed as an independent research & engineering project exploring Computer Vision and Stochastic Game AI.

> **Design & Tooling Note**: The core algorithmic architecture—including the OpenCV screen perception pipeline, topological contour classifier, recursive Expectimax search tree, and headless genetic algorithm—was engineered and implemented from scratch in Python. Modern generative AI design tools were leveraged as a productivity accelerator to refine the Next.js visual dashboard layout and CSS aesthetics.

This project is licensed under the [MIT License](LICENSE). Feel free to fork, experiment, and build upon it!
