# StreamBox — Live HLS Video Streaming

A modern, high-performance live streaming web application built with **FastAPI**, **Video.js 8**, **ImageKit-inspired Video Player Theme**, and the **Globo Codex** dark design system.

![StreamBox Preview](static/images/space_station.jpg)

---

## ✨ Features

- **Adaptive HLS Playback**: Integrated Video.js 8 with `videojs-http-source-selector` and `videojs-contrib-quality-levels` for real-time resolution switching (Auto, 1080p, 720p, 480p, 360p).
- **Akamai CDN & CORS Proxy**: Built-in async HLS manifest and transport stream proxy (`/api/stream/proxy`) that rewrites child manifests and relative segment URLs while handling CORS headers and Akamai token expiration.
- **Globo Codex Dark Canvas**: Dark-first streaming aesthetic optimized for high contrast, OLED panels, and distraction-free viewing.
- **Dynamic Stream Switcher**: Interactive modal for inputting custom HLS/M3U8 URLs and auth tokens on the fly.
- **Interactive UI**: Featuring search overlay, quick channel rail, custom keyboard shortcuts (Space, F, M, Arrow Keys), and cast controls.

---

## 🚀 Quick Start

### 1. Requirements

- Python 3.10+ (or [uv](https://github.com/astral-sh/uv))

### 2. Setup & Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/saurabh-yadav-ggu/cricket_live_stream.git
cd cricket_live_stream
```

Using `uv`:
```bash
uv sync
uv run uvicorn main:app --reload --port 8000
```

Or using standard `pip`:
```bash
pip install "fastapi[standard]" httpx
uvicorn main:app --reload --port 8000
```

### 3. Open in Browser

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to start watching the live stream.

---

## 🛠 Project Structure

```text
├── main.py                  # FastAPI application & HLS proxy server
├── pyproject.toml           # Project dependencies & metadata
├── templates/
│   └── index.html           # Main player interface template
├── static/
│   ├── css/
│   │   ├── style.css        # Globo Codex dark styling
│   │   ├── imagekit-theme.css
│   │   └── video-js.min.css
│   ├── js/
│   │   ├── main.js          # Player initialization, shortcuts, & UI controls
│   │   ├── video.min.js     # Video.js 8 core
│   │   ├── videojs-contrib-quality-levels.min.js
│   │   └── videojs-http-source-selector.min.js
│   └── images/              # Hero cards & placeholder media
└── design.md                # Globo Codex design system documentation
```

---

## 📄 License

MIT License. Crafted with ❤️ by [Saurabh Yadav](https://github.com/saurabh-yadav-ggu).
