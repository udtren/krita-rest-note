# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 2026-05-12
### Changed
- **Responsive icon buttons** — Pause, Reset, and Config buttons now scale in size with the docker, matching the dynamic font scaling behaviour. Button size is derived from the same `time_pt` value used for the clock label (ratio 0.5×, clamped 16–64 px).

## 2026-05-11 — Initial release
### Added
- **Docker panel** — Responsive widget showing current state, countdown timer, and next eye break time. Labels scale dynamically with the docker size.
- **Work / break cycle** — Configurable countdown (default: 50 min work / 10 min break). Triggers a fullscreen overlay when the work timer expires.
- **Break overlay** — Fullscreen dark overlay that fades in over 30 seconds. "Resume work" progress button becomes clickable only after the full break duration elapses. A "Skip" button allows immediate dismissal.
- **20-20-20 eye break reminders** — Optional micro-break toast (default: every 20 min, 20 sec duration) that appears in the bottom-right corner without blocking input or stealing focus. Skipped automatically if the next big break is within a configurable threshold.
- **Pause / Resume / Reset controls** — Icon buttons in the docker. Pause freezes both timers; Reset cancels any active overlay or toast and restarts from zero.
- **Configuration dialog** — Settings grouped by section:
  - *Work / Break cycle* — work duration, break duration
  - *Eye break reminder* — enable toggle, interval, duration, skip threshold
  - *Overlay appearance* — title, message, and skip button font sizes
  - *Toast appearance* — margin, width, height, title and message font sizes
- **Persistent settings** — Saved to `rest_note/config/main.json`.
