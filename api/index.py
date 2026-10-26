import sys
import os
import traceback
from pathlib import Path

# Add api directory, project root directory and /var/task to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent

for p in [str(CURRENT_DIR), str(ROOT_DIR), "/var/task", "/var/task/api"]:
    if p not in sys.path and Path(p).exists():
        sys.path.insert(0, p)

try:
    from main import app
except Exception as e:
    tb = traceback.format_exc()
    print("FATAL ERROR BOOTING FASTAPI ON VERCEL:\n", tb)
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "OPTIONS", "HEAD"])
    async def boot_error_handler(path: str = ""):
        return PlainTextResponse(f"FastAPI Vercel Boot Error:\n\n{tb}", status_code=500)
