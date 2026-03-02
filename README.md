# Operation SKYE-X — Autonomous Aerial Robotics Hackathon

> **Aerial Robotics Club | Y25 Recruitment Hackathon**

Welcome to **Operation SKYE-X**, a multi-level autonomous drone simulation challenge. Your mission is to program an intelligent flight controller for a quadcopter drone navigating a contested 2D aerial environment.

---

## Challenge Structure

| Level | Title | Description |
|-------|-------|-------------|
| [Level 1](./Hackathon/Level1/PROBLEM_STATEMENT.md) | **Operation SKYE-X: Search & Pursuit** | Explore the map, find an evasive target, and track it under sensor limitations |
| [Level 2](./Hackathon/Level2/PROBLEM_STATEMENT.md) | **Operation Touchdown: Precision Landing** | A harder variant with new constraints — unlocked after Level 1 |
| [Level 3](./Hackathon/Level3/PROBLEM_STATEMENT.md) | **Project MIRAGE: Hybrid Marker Steganography** | Create a single image that shows a decoy at high altitude and a secret ArUco marker at low altitude |

---

## Environment Setup

### Requirements
```bash
pip install pygame
pip install opencv-contrib-python numpy    # Level 3
```

### Running Simulation
```bash
# Level 1 — Search & Pursuit
cd Hackathon/Level1
python skye_controller.py

# Level 2 — Precision Landing
cd Hackathon/Level2
python simulator.py          # Demo mode (built-in controller)
python simulator.py --c      # Your controller (reads commands.txt)

# Level 3 — Project MIRAGE
cd Hackathon/Level3
python generator.py far_target_decoy.png aruco_markers/aruco_id_X.png X hybrid_marker.png
python simulator.py hybrid_marker.png 30   # View at 30m — should show H symbol
python simulator.py hybrid_marker.png 2    # View at 2m — should show ArUco
```

---

## Submission Guidelines

### Level 1
- Only modify `skye_controller.py` — **do not modify `skye_env.py` or `config.py`**
- Submit your final `skye_controller.py` with a short write-up explaining your approach

### Level 2
- Write a controller (Python or C++) that reads `camera_pixels.txt` and writes velocity commands to `commands.txt`
- Submit your controller source file with a short write-up explaining your approach

### Level 3
- Submit a GitHub repository with: `generator.py`, `hybrid_marker.png`, `viewer.py`, `visual_check.py`, `drone_view_2.0m.png`, `drone_view_30.0m.png`, and `report.pdf`
- `viewer.py` and `visual_check.py` must be **built from scratch** — they are not provided
- `report.pdf` (max 2 pages) must include σ values, mathematical reasoning, and GSD calculation

---

## Scoring

### Level 1 — Search & Pursuit

| Metric | How It's Measured |
|--------|-------------------|
| **Tracking Score** | +1 per timestep the target is within `TRACKING_RADIUS` (70px) |
| **Survival** | Score is forfeited on crash |
| **Mission Duration** | Max `3000` timesteps |

### Level 2 — Precision Landing

| Metric | How It's Measured |
|--------|-------------------|
| **Landing Accuracy** | Distance (m) from platform center at touchdown |
| **Success Threshold** | ≤ `0.35 m` from center = **SUCCESS** |
| **Precision Bonus** | `< 0.1 m` = exceptional |

### Level 3 — Project MIRAGE

| Criterion | Weightage | How It's Measured |
|-----------|-----------|-------------------|
| **ArUco ID_X detected at ≤ 5m** | 40% | Image shrunk to 5m pixel size, ArUco detection run |
| **ArUco ID_X hidden at ≥ 30m** | 30% | Image shrunk to 30m pixel size, ArUco detection run |
| **Visual quality — no ghosting** | 15% | Judging script at 30m; visual inspection for ArUco bleed-through |
| **Math justification in report** | 15% | σ values backed by GSD/Nyquist calculations, not trial and error |
