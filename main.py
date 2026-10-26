import asyncio
from contextlib import asynccontextmanager
import json
import logging
import mimetypes
import os
import re
import urllib.parse
from pathlib import Path
from typing import Optional, Any, Dict, List

import httpx
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, JSONResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from stream_sync import sync_manager, STANDBY_STREAM_URL

logger = logging.getLogger("stream_video")

# Project base directory
BASE_DIR = Path(__file__).resolve().parent

# Lifespan manager: instant zero-latency boot
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure local disk catalog is loaded immediately (<1ms)
    sync_manager.load_cached_catalog_sync()
    yield

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

# Global exception shield to prevent container-level crashes
@app.middleware("http")
async def global_exception_shield(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Global unhandled request error: {tb}")
        return PlainTextResponse(f"StreamBox Server Error:\n\n{tb}", status_code=500)

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
async def root(request: Request):
    # If a url query parameter is present, delegate directly to stream proxy
    if "url" in request.query_params:
        return await stream_proxy(request, request.query_params["url"])

    live_url = get_current_live_url()
    try:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "default_stream_url": live_url,
                "active_event": sync_manager.active_event_name
            }
        )
    except Exception as exc:
        logger.error(f"Template rendering failed: {exc}")
        html_fallback_path = templates_dir / "index.html"
        if html_fallback_path.exists():
            html_content = html_fallback_path.read_text(encoding="utf-8")
            return HTMLResponse(content=html_content)
        return HTMLResponse(content=f"<html><body><h1>StreamBox Live</h1><p>Active Event: {sync_manager.active_event_name}</p></body></html>")


@app.get("/health")
@app.get("/healthz")
async def health_check():
    """AWS ALB, App Runner, ECS, and Docker container healthcheck endpoint."""
    return {
        "status": "healthy",
        "service": "streambox",
        "active_stream": sync_manager.active_live_stream is not None
    }


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


# Shared persistent connection client for HLS reverse proxying
_proxy_client: Optional[httpx.AsyncClient] = None
_client_loop: Any = None

def get_proxy_client() -> httpx.AsyncClient:
    global _proxy_client, _client_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _proxy_client is None or _proxy_client.is_closed or _client_loop != current_loop:
        _proxy_client = httpx.AsyncClient(
            verify=False,
            timeout=httpx.Timeout(16.0, connect=5.0),
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=40, max_connections=80)
        )
        _client_loop = current_loop
    return _proxy_client


@app.options("/api/stream/proxy")
@app.options("/stream/proxy")
async def stream_proxy_options():
    """Handles CORS preflight requests for Video.js cross-origin playback."""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        }
    )


@app.head("/api/stream/proxy")
@app.head("/stream/proxy")
async def stream_proxy_head(request: Request, url: str = Query(...)):
    """Handles HEAD probe requests from Video.js VHS player engine."""
    is_m3u8 = ".m3u8" in url.lower()
    return Response(
        status_code=200,
        media_type="application/vnd.apple.mpegurl" if is_m3u8 else "video/MP2T",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Expose-Headers": "Content-Length, Content-Range",
        }
    )


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
    3. Streams video chunks with connection pooling and Range request support.
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

    # Standard clean browser request headers (DO NOT forward X-Forwarded-For or True-Client-IP as Akamai blocks them with 403)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
    }
    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    client = get_proxy_client()
    is_manifest = (".m3u8" in target_url.lower())

    try:
        req = client.build_request("GET", target_url, headers=headers)
        upstream_resp = await client.send(req, stream=True)
    except httpx.RequestError as exc:
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
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Expose-Headers": "Content-Length, Content-Range",
                "Cache-Control": "no-cache, no-store, must-revalidate",
            }
        )
    else:
        # TS segment or binary stream
        body_bytes = await upstream_resp.aread()

        headers_out = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Expose-Headers": "Content-Length, Content-Range",
            "Cache-Control": "public, max-age=3600",
            "Content-Length": str(len(body_bytes)),
        }
        if "content-range" in upstream_resp.headers:
            headers_out["Content-Range"] = upstream_resp.headers["content-range"]

        return Response(
            content=body_bytes,
            status_code=upstream_resp.status_code,
            media_type=content_type or "video/MP2T",
            headers=headers_out
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=False)
