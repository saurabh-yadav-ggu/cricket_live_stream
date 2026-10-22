import re
import urllib.parse
from pathlib import Path
import httpx
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="StreamBox - Stream Video")

# Static files configuration
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates configuration
templates_dir = (
    BASE_DIR / "templates"
    if (BASE_DIR / "templates").exists()
    else (BASE_DIR / "template" if (BASE_DIR / "template").exists() else BASE_DIR / "templates")
)
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Default user-provided live HLS stream URL (Akamai signed stream)
DEFAULT_STREAM_URL = (
    "https://sonydaime.akamaized.net/hls/live/2119921/cricodi_2210/HIN/std_lrh-800300010.m3u8"
    "?hdnea=exp=1792700326~acl=/*~id=89575885627351036019877985996111~hmac=48f8e7b8b2d4e6e264fde915a7a48abc6341d1d3a34c237c4190dcdd2e580a99"
)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"default_stream_url": DEFAULT_STREAM_URL}
    )


@app.get("/api/stream/default")
async def get_default_stream():
    """Returns the default active HLS stream URL for client playback without exposing secrets."""
    return {
        "title": "Chrono Station • Live Feed (HLS)",
        "stream_url": DEFAULT_STREAM_URL,
        "proxied_url": f"/api/stream/proxy?url={urllib.parse.quote(DEFAULT_STREAM_URL, safe='')}",
        "protocol": "hls",
        "is_live": True,
    }


@app.get("/api/stream/proxy")
async def stream_proxy(url: str = Query(..., description="Target HLS manifest or segment URL")):
    """
    High-performance HLS proxy that:
    1. Forwards signed requests to CDN while resolving browser CORS limitations.
    2. Dynamically rewrites child playlists and relative segment URLs.
    3. Streams video chunks without memory bloat.
    4. Accurately reports HTTP 401/403 token expiration and network errors.
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

    client = httpx.AsyncClient(verify=False, timeout=15.0, follow_redirects=True)

    try:
        req = client.build_request("GET", target_url, headers=headers)
        upstream_resp = await client.send(req, stream=True)
    except httpx.RequestError as exc:
        await client.aclose()
        return JSONResponse(
            content={
                "error": "Upstream connection failure",
                "error_code": "NETWORK_ERROR",
                "details": str(exc),
            },
            status_code=502,
            headers={"Access-Control-Allow-Origin": "*"}
        )

    # Check for authentication / token expiration
    if upstream_resp.status_code in (401, 403):
        await upstream_resp.aread()
        await client.aclose()
        return JSONResponse(
            content={
                "error": "Signed token expired or stream access forbidden",
                "error_code": "TOKEN_EXPIRED",
                "status_code": upstream_resp.status_code,
                "message": "The authentication token in the signed URL has expired or is invalid.",
            },
            status_code=upstream_resp.status_code,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    elif upstream_resp.status_code >= 400:
        await upstream_resp.aread()
        await client.aclose()
        return JSONResponse(
            content={
                "error": f"Upstream HTTP error {upstream_resp.status_code}",
                "error_code": "UPSTREAM_ERROR",
                "status_code": upstream_resp.status_code,
            },
            status_code=upstream_resp.status_code,
            headers={"Access-Control-Allow-Origin": "*"}
        )

    content_type = upstream_resp.headers.get("content-type", "")
    is_m3u8 = (".m3u8" in target_url.lower()) or ("mpegurl" in content_type.lower())

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
        async def stream_chunks():
            try:
                async for chunk in upstream_resp.aiter_bytes():
                    yield chunk
            finally:
                await upstream_resp.aclose()
                await client.aclose()

        headers_out = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Cache-Control": "public, max-age=3600",
        }
        if "content-length" in upstream_resp.headers:
            headers_out["Content-Length"] = upstream_resp.headers["content-length"]

        return StreamingResponse(
            stream_chunks(),
            status_code=upstream_resp.status_code,
            media_type=content_type or "video/MP2T",
            headers=headers_out
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
