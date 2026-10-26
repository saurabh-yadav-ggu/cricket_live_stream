import sys
import traceback
from pathlib import Path

# Add project root directory and /var/task to sys.path so modules and templates can be resolved on Vercel
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

VAR_TASK = Path("/var/task")
if VAR_TASK.exists() and str(VAR_TASK) not in sys.path:
    sys.path.insert(0, str(VAR_TASK))

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from main import app
    handler = app
except Exception as e:
    tb = traceback.format_exc()
    print("FATAL ERROR BOOTING FASTAPI ON VERCEL:\n", tb)
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse
    fallback_app = FastAPI()

    @fallback_app.api_route("/{path:path}", methods=["GET", "POST", "OPTIONS", "HEAD"])
    async def boot_error_handler(path: str):
        return PlainTextResponse(f"FastAPI Vercel Boot Error:\n{tb}", status_code=500)

    handler = fallback_app
    app = fallback_app
