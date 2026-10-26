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

## ☁️ AWS Deployment

StreamBox is fully configured for production deployment on **AWS** across multiple architectures:

- **AWS App Runner (Recommended)**: 100% managed container service with automatic SSL, zero server management, and auto-scaling.
- **AWS Lightsail / EC2 with Docker**: Most budget-friendly option ($3.50/mo or free tier) using `docker compose` and Nginx.
- **AWS ECS (Fargate)**: Enterprise container scaling using ECR and ECS.

👉 **See the complete step-by-step guide in [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md).**

### Quick Docker Launch:
```bash
docker compose up -d --build
```

---

## 🛠 Project Structure

```text
├── main.py                  # FastAPI application & HLS proxy server
├── stream_sync.py           # Background sync & stream fallback manager
├── Dockerfile               # Production multi-stage Docker container
├── docker-compose.yml       # Local & EC2 container orchestration
├── apprunner.yaml           # AWS App Runner native deployment manifest
├── ecs-task-definition.json # AWS ECS Fargate task definition
├── nginx.conf               # High-performance Nginx reverse proxy configuration
├── deploy-ec2.sh            # 1-click automated setup script for Ubuntu EC2/Lightsail
├── AWS_DEPLOYMENT_GUIDE.md  # Detailed AWS deployment documentation
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
