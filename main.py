import asyncio
from contextlib import asynccontextmanager
import json
import logging
import mimetypes
import re
import urllib.parse
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from stream_sync import sync_manager, STANDBY_STREAM_URL

logger = logging.getLogger("stream_video")

# Robust BASE_DIR resolution for both local and Vercel serverless environments
BASE_DIR = Path(__file__).resolve().parent
for candidate in [BASE_DIR, BASE_DIR.parent, Path.cwd(), Path("/var/task")]:
    if (candidate / "templates").exists() and (candidate / "static").exists():
        BASE_DIR = candidate
        break

# Lifespan manager: runs startup sync and periodic background polling
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initial sync on boot
    try:
        await sync_manager.sync()
    except Exception as e:
        logger.error(f"Initial stream sync error: {e}")

    # Background sync task (polls GitHub stream source every 3 minutes)
    async def periodic_sync_worker():
        while True:
            await asyncio.sleep(180)  # 3 minutes
            try:
                await sync_manager.sync()
            except Exception as e:
                logger.warning(f"Periodic GitHub stream sync error: {e}")

    sync_task = asyncio.create_task(periodic_sync_worker())
    try:
        yield
    finally:
        sync_task.cancel()
        try:
            await sync_task
        except asyncio.CancelledError:
            pass

app = FastAPI(title="StreamBox - Stream Video", lifespan=lifespan, redirect_slashes=False)

# Enable CORS for cross-origin player requests and preflight checks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files configuration
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    app.mount("/api/static", StaticFiles(directory=str(static_dir)), name="api_static")

@app.middleware("http")
async def static_fallback_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/static/"):
        relative_path = path[len("/static/"):]
        file_path = static_dir / relative_path
        if file_path.exists() and file_path.is_file():
            from fastapi.responses import FileResponse
            content_type, _ = mimetypes.guess_type(str(file_path))
            return FileResponse(file_path, media_type=content_type or "application/octet-stream")
    return await call_next(request)

# Templates configuration
templates_dir = BASE_DIR / "templates"
if not templates_dir.exists():
    templates_dir = BASE_DIR / "template"
templates = Jinja2Templates(directory=str(templates_dir))


def get_current_live_url() -> str:
    """Returns the freshest verified stream URL or standby fallback."""
    return sync_manager.active_live_stream or STANDBY_STREAM_URL


@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
@app.get("/api", response_class=HTMLResponse)
@app.get("/api/", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
@app.get("/api/index.py", response_class=HTMLResponse)
async def root(request: Request):
    live_url = get_current_live_url()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "default_stream_url": live_url,
            "active_event": sync_manager.active_event_name
        }
    )


@app.get("/api/stream/status")
@app.get("/stream/status")
async def get_stream_status():
    """Returns real-time sync metrics, token expiration countdown, and active match info."""
    return sync_manager.get_status()


@app.get("/api/stream/sync")
@app.post("/api/stream/sync")
async def trigger_stream_sync():
    """Forces an immediate synchronization with the GitHub stream repository."""
    result = await sync_manager.sync()
    return {
        "status": "synchronized",
        "result": result,
        "current_status": sync_manager.get_status()
    }


@app.get("/api/stream/live")
@app.get("/stream/live")
async def get_live_stream():
    """Returns the currently active live match stream URL and metadata."""
    live_url = get_current_live_url()
    proxied_url = f"/api/stream/proxy?url={urllib.parse.quote(live_url, safe='')}"
    status = sync_manager.get_status()
    return {
        "title": sync_manager.active_event_name,
        "stream_url": live_url,
        "proxied_url": proxied_url,
        "is_live": status["has_real_stream"],
        "token_valid": status["token_valid"],
        "token_seconds_left": status["token_seconds_left"],
        "last_sync_source": status["last_sync_source"]
    }


@app.get("/api/stream/default")
@app.get("/stream/default")
async def get_default_stream():
    """Returns the default active HLS stream URL for client playback without exposing secrets."""
    live_url = get_current_live_url()
    return {
        "title": sync_manager.active_event_name,
        "stream_url": live_url,
        "proxied_url": f"/api/stream/proxy?url={urllib.parse.quote(live_url, safe='')}",
        "protocol": "hls",
        "is_live": sync_manager.active_live_stream != STANDBY_STREAM_URL,
    }


@app.get("/api/channels")
@app.get("/channels")
async def get_channels(
    category: str = Query("all", description="Category filter"),
    query: str = Query("", description="Search term"),
    limit: int = Query(600, description="Max channels")
):
    """Returns live channels synced dynamically from GitHub sonyliv.json."""
    channels = sync_manager.cached_channels
    if not channels and sync_manager.static_channels_path.exists():
        try:
            with open(sync_manager.static_channels_path, "r", encoding="utf-8") as f:
                channels = json.load(f)
                sync_manager.cached_channels = channels
        except Exception:
            channels = []

    filtered = channels
    if category and category.lower() != "all":
        cat_lower = category.lower()
        if cat_lower == "hindi":
            filtered = [c for c in filtered if (c.get("language_code") or "").lower() == "hin"]
        elif cat_lower == "english":
            filtered = [c for c in filtered if (c.get("language_code") or "").lower() == "eng"]
        elif cat_lower == "regional":
            filtered = [c for c in filtered if (c.get("language_code") or "").lower() in ["tam", "kan", "tel", "mal"]]
        else:
            filtered = [c for c in filtered if c.get("category") == cat_lower]

    if query:
        q = query.lower().strip()
        filtered = [
            c for c in filtered
            if q in c.get("name", "").lower()
            or q in c.get("raw_name", "").lower()
            or q in c.get("language", "").lower()
            or q in c.get("broadcast_channel", "").lower()
        ]

    return {
        "total": len(filtered),
        "source": sync_manager.last_sync_source,
        "channels": filtered[:limit]
    }


@app.get("/api/stream/proxy")
@app.get("/stream/proxy")
async def stream_proxy(
    request: Request,
    url: str = Query(..., description="Target HLS manifest or segment URL")
):
    """
    High-performance HLS reverse proxy that:
    1. Forwards signed requests to Akamai/CDN while resolving browser CORS limitations.
    2. Dynamically rewrites child playlists and relative segment URLs.
    3. Streams video chunks without memory bloat.
    4. Resilient Fallback: If an expired token returns 401/403, triggers background sync
       and returns a valid fallback stream instead of crashing the player with format errors.
    """
    try:
        target_url = urllib.parse.unquote(url)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid stream URL format")

    parsed = urllib.parse.urlparse(target_url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only HTTP/HTTPS streams supported")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }

    # Forward client IP for geo-targeted Akamai tokens
    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.headers.get("x-real-ip", "").strip()
        or (request.client.host if request.client else "")
    )
    if client_ip and client_ip not in ("127.0.0.1", "localhost", "::1"):
        headers["X-Forwarded-For"] = client_ip
        headers["True-Client-IP"] = client_ip

    client = httpx.AsyncClient(verify=False, timeout=12.0, follow_redirects=True)

    is_manifest = (".m3u8" in target_url.lower())

    try:
        req = client.build_request("GET", target_url, headers=headers)
        upstream_resp = await client.send(req, stream=True)
    except httpx.RequestError as exc:
        await client.aclose()
        # If manifest failed due to network error, fall back to standby
        if is_manifest:
            logger.warning(f"Upstream request failed ({exc}), falling back to standby stream")
            fallback_target = f"/api/stream/proxy?url={urllib.parse.quote(STANDBY_STREAM_URL, safe='')}"
            return RedirectResponse(url=fallback_target, status_code=307)
        return JSONResponse(
            content={"error": "Upstream connection failure", "details": str(exc)},
            status_code=502,
            headers={"Access-Control-Allow-Origin": "*"}
        )

    # Handle token expiration (HTTP 401 / 403 / 404) gracefully
    if upstream_resp.status_code in (401, 403, 404):
        await upstream_resp.aread()
        await client.aclose()

        # Trigger background sync to attempt acquiring fresh tokens from GitHub
        asyncio.create_task(sync_manager.sync())

        # If an M3U8 manifest was requested, redirect to working fallback so Video.js doesn't crash
        if is_manifest:
            active_live = sync_manager.active_live_stream
            if active_live and active_live != target_url and sync_manager.is_token_valid(active_live):
                fallback_url = f"/api/stream/proxy?url={urllib.parse.quote(active_live, safe='')}"
            else:
                fallback_url = f"/api/stream/proxy?url={urllib.parse.quote(STANDBY_STREAM_URL, safe='')}"
            return RedirectResponse(
                url=fallback_url,
                status_code=307,
                headers={
                    "X-Stream-Status": "standby-fallback",
                    "Access-Control-Allow-Origin": "*"
                }
            )

        return JSONResponse(
            content={
                "error": "Stream access expired or unavailable",
                "status_code": upstream_resp.status_code,
                "message": "The stream token for this match is expired or not currently broadcasting."
            },
            status_code=upstream_resp.status_code,
            headers={"Access-Control-Allow-Origin": "*"}
        )

    content_type = upstream_resp.headers.get("content-type", "")
    is_m3u8 = is_manifest or ("mpegurl" in content_type.lower())

    if is_m3u8:
        # Read full playlist and rewrite relative lines
        body_bytes = await upstream_resp.aread()
        await client.aclose()

        try:
            content_str = body_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content_str = body_bytes.decode("latin1")

        lines = content_str.splitlines()
        rewritten_lines = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                rewritten_lines.append("")
                continue

            if line_str.startswith("#"):
                # Handle #EXT-X-MEDIA or #EXT-X-KEY URI="..."
                if 'URI="' in line_str:
                    def replace_uri(match):
                        sub_uri = match.group(1)
                        resolved_sub = urllib.parse.urljoin(target_url, sub_uri)
                        proxied = f"/api/stream/proxy?url={urllib.parse.quote(resolved_sub, safe='')}"
                        return f'URI="{proxied}"'
                    line_str = re.sub(r'URI="([^"]+)"', replace_uri, line_str)
                rewritten_lines.append(line_str)
            else:
                # Relative or absolute segment/child playlist URL
                resolved_child = urllib.parse.urljoin(target_url, line_str)
                proxied_url = f"/api/stream/proxy?url={urllib.parse.quote(resolved_child, safe='')}"
                rewritten_lines.append(proxied_url)

        final_playlist = "\n".join(rewritten_lines) + "\n"
        return Response(
            content=final_playlist,
            media_type="application/vnd.apple.mpegurl",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Cache-Control": "no-cache, no-store, must-revalidate",
            }
        )
    else:
        # TS segment or binary stream
        body_bytes = await upstream_resp.aread()
        await client.aclose()

        headers_out = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Cache-Control": "public, max-age=3600",
            "Content-Length": str(len(body_bytes)),
        }

        return Response(
            content=body_bytes,
            status_code=upstream_resp.status_code,
            media_type=content_type or "video/MP2T",
            headers=headers_out
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
