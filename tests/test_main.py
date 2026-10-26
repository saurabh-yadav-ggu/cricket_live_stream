import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Verify /health returns 200 OK and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert data.get("service") == "streambox"


def test_healthz_alias():
    """Verify Kubernetes / AWS ALB healthz alias returns 200 OK."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


def test_root_page():
    """Verify home page loads HTML interface."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "StreamBox" in response.text or "video-js" in response.text


def test_stream_status():
    """Verify stream synchronization status endpoint."""
    response = client.get("/api/stream/status")
    assert response.status_code == 200
    data = response.json()
    assert "last_sync_source" in data
    assert "has_real_stream" in data


def test_live_stream_info():
    """Verify live stream endpoint returns stream metadata."""
    response = client.get("/api/stream/live")
    assert response.status_code == 200
    data = response.json()
    assert "stream_url" in data
    assert "proxied_url" in data
    assert "title" in data


def test_channels_catalog():
    """Verify channels catalog returns channel list."""
    response = client.get("/api/channels")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "channels" in data
    assert isinstance(data["channels"], list)


def test_channels_filter_category():
    """Verify channels can be filtered by category or language."""
    response = client.get("/api/channels?category=hindi")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("channels"), list)


def test_stream_proxy_invalid_url():
    """Verify stream proxy rejects non-HTTP/HTTPS schemes."""
    response = client.get("/api/stream/proxy?url=ftp://example.com/test.m3u8")
    assert response.status_code == 400
