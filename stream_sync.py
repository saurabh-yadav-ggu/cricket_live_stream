"""
StreamSync Module for StreamBox
Handles dynamic synchronization with external GitHub repository:
https://github.com/saurabh-yadav-ggu/SONYLIV-AUTO-UPDATED-PLAYLIST.git

Features:
- Periodic background polling of sonyliv.json & sonyliv.m3u
- Multiple fallback sources (saurabh-yadav-ggu, sayanpal514-hue, local clone)
- Akamai token expiration inspection and live probing
- Standby / slate stream fallback to prevent "format not supported" errors
- Automatic catalog generation for static/channels.json
"""

import asyncio
import json
import logging
import re
import time
import urllib.parse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import httpx

logger = logging.getLogger("stream_sync")

BASE_DIR = Path(__file__).resolve().parent

# GitHub stream source endpoints
GITHUB_PRIMARY_JSON = "https://raw.githubusercontent.com/sayanpal514-hue/SONYLIV-AUTO-UPDATED-PLAYLIST/main/sonyliv.json"
GITHUB_PRIMARY_M3U = "https://raw.githubusercontent.com/sayanpal514-hue/SONYLIV-AUTO-UPDATED-PLAYLIST/main/sonyliv.m3u"
GITHUB_FALLBACK_JSON = "https://raw.githubusercontent.com/saurabh-yadav-ggu/SONYLIV-AUTO-UPDATED-PLAYLIST/main/sonyliv.json"
GITHUB_FALLBACK_M3U = "https://raw.githubusercontent.com/saurabh-yadav-ggu/SONYLIV-AUTO-UPDATED-PLAYLIST/main/sonyliv.m3u"

# High-reliability standby HLS stream when no match is live
STANDBY_STREAM_URL = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"

# Language display mapping
LANG_MAP = {
    "HIN": "Hindi",
    "ENG": "English",
    "TAM": "Tamil",
    "TEL": "Telugu",
    "KAN": "Kannada",
    "MAL": "Malayalam",
    "BEN": "Bengali",
}

class StreamSyncManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.static_channels_path = base_dir / "static" / "channels.json"
        self.local_repo_path = base_dir / "SONYLIV-AUTO-UPDATED-PLAYLIST"
        
        self.last_sync_time: Optional[float] = None
        self.last_sync_source: str = "none"
        self.cached_matches: List[Dict[str, Any]] = []
        self.cached_channels: List[Dict[str, Any]] = []
        self.active_live_stream: Optional[str] = None
        self.active_event_name: str = "Sony LIV Sports Feed"
        self.token_expiry: Optional[int] = None
        self._lock: Optional[asyncio.Lock] = None

        # Synchronously load cached channels on instantiation for instant zero-latency cold starts
        self.load_cached_catalog_sync()

    def load_cached_catalog_sync(self):
        """Immediately loads channels from channels.json for zero-latency boot."""
        candidates = [
            self.static_channels_path,
            self.base_dir / "static" / "channels.json",
            Path("/tmp/channels.json")
        ]
        for p in candidates:
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        self.cached_channels = data
                        self.last_sync_source = f"disk:{p.name}"
                        self.last_sync_time = time.time()
                        for ch in data:
                            if ch.get("is_live") and ch.get("url"):
                                self.active_live_stream = ch["url"]
                                self.active_event_name = ch.get("name", "Sony LIV Live Feed")
                                self.token_expiry = self.parse_token_expiry(ch["url"])
                                break
                        logger.info(f"Loaded {len(data)} channels from {p}")
                        return
                except Exception as exc:
                    logger.warning(f"Failed to load cached channels from {p}: {exc}")

    @property
    def lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
        
    def parse_token_expiry(self, url: str) -> Optional[int]:
        """Extracts exp=<timestamp> from Akamai / signed URL."""
        if not url:
            return None
        match = re.search(r'\bexp=(\d+)\b', url)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None

    def is_token_valid(self, url: str) -> bool:
        """Checks if URL expiration timestamp is in the future."""
        expiry = self.parse_token_expiry(url)
        if expiry is None:
            return True  # If not tokenized, assume standard stream
        # Require at least 60 seconds of validity remaining
        return expiry > (time.time() + 60)

    async def probe_stream(self, url: str) -> bool:
        """Lightweight check to verify if the stream manifest responds with 200."""
        if not url:
            return False
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "*/*"
        }
        try:
            async with httpx.AsyncClient(timeout=4.0, verify=False, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                return resp.status_code == 200 and ("#EXTM3U" in resp.text[:100])
        except Exception:
            return False

    async def fetch_remote_json(self) -> Tuple[Optional[dict], str]:
        """Fetches sonyliv.json from primary GitHub, fallback GitHub, or local clone."""
        async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
            # 1. Primary GitHub repo (sayanpal514-hue)
            try:
                r = await client.get(GITHUB_PRIMARY_JSON, headers={"Cache-Control": "no-cache"})
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, dict) and "matches" in data:
                        return data, "github:sayanpal514-hue"
            except Exception as e:
                logger.warning(f"Primary GitHub fetch failed: {e}")

            # 2. Fallback upstream repo (saurabh-yadav-ggu)
            try:
                r = await client.get(GITHUB_FALLBACK_JSON, headers={"Cache-Control": "no-cache"})
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, dict) and "matches" in data:
                        return data, "github:saurabh-yadav-ggu"
            except Exception as e:
                logger.warning(f"Fallback GitHub fetch failed: {e}")

        # 3. Local clone file
        local_json_file = self.local_repo_path / "sonyliv.json"
        if local_json_file.exists():
            try:
                with open(local_json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data, "local_repo"
            except Exception as e:
                logger.warning(f"Local repo sonyliv.json read error: {e}")

        return None, "none"

    async def fetch_remote_m3u_live_url(self) -> Optional[Tuple[str, str]]:
        """Parses active live stream URL from sonyliv.m3u if present."""
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            for url in [GITHUB_PRIMARY_M3U, GITHUB_FALLBACK_M3U]:
                try:
                    r = await client.get(url, headers={"Cache-Control": "no-cache"})
                    if r.status_code == 200:
                        lines = r.text.strip().splitlines()
                        for i, line in enumerate(lines):
                            if line.startswith("#EXTINF") and i + 1 < len(lines):
                                stream_url = lines[i + 1].strip()
                                if stream_url.startswith("http"):
                                    # Extract title from EXTINF
                                    title = line.split(",")[-1].strip() if "," in line else "Live Match"
                                    return stream_url, title
                except Exception:
                    continue

        # Check local sonyliv.m3u
        local_m3u = self.local_repo_path / "sonyliv.m3u"
        if local_m3u.exists():
            try:
                with open(local_m3u, "r", encoding="utf-8") as f:
                    lines = f.read().strip().splitlines()
                    for i, line in enumerate(lines):
                        if line.startswith("#EXTINF") and i + 1 < len(lines):
                            stream_url = lines[i + 1].strip()
                            if stream_url.startswith("http"):
                                title = line.split(",")[-1].strip() if "," in line else "Live Match"
                                return stream_url, title
            except Exception:
                pass

        return None

    def find_recent_valid_commit_stream(self) -> Optional[Tuple[str, str]]:
        """Scans recent git commits in local repo for an active Akamai stream with the longest remaining validity."""
        if not self.local_repo_path.exists():
            return None
        valid_candidates = []
        try:
            # 1. Check sonyliv.m3u history
            diff_out = subprocess.check_output(
                ["git", "log", "-S", "sonydaime.akamaized.net", "-n", "10", "-p", "sonyliv.m3u"],
                cwd=self.local_repo_path,
                stderr=subprocess.DEVNULL
            ).decode(errors="ignore")
            
            lines = diff_out.splitlines()
            for idx, line in enumerate(lines):
                clean_l = line.lstrip("+-").strip()
                if clean_l.startswith("http") and "akamaized.net" in clean_l:
                    stream_url = clean_l
                    if self.is_token_valid(stream_url):
                        exp = self.parse_token_expiry(stream_url) or 0
                        # Try to find corresponding title from previous EXTINF
                        title = "Sony LIV Live Match Feed"
                        for prev in range(max(0, idx - 4), idx):
                            if "EXTINF" in lines[prev]:
                                title = lines[prev].split(",")[-1].strip()
                                break
                        valid_candidates.append((exp, stream_url, title))

            # 2. Check sonyliv.json commits
            commits = subprocess.check_output(
                ["git", "log", "-S", "isLive", "--format=%H", "-n", "15"],
                cwd=self.local_repo_path,
                stderr=subprocess.DEVNULL
            ).decode().split()
            for c in commits:
                try:
                    raw = subprocess.check_output(
                        ["git", "show", f"{c}:sonyliv.json"],
                        cwd=self.local_repo_path,
                        stderr=subprocess.DEVNULL
                    )
                    d = json.loads(raw)
                    for m in d.get("matches", []):
                        if m.get("isLive") and (m.get("dai_url") or m.get("video_url")):
                            url = m.get("dai_url") or m.get("video_url")
                            if self.is_token_valid(url):
                                exp = self.parse_token_expiry(url) or 0
                                title = m.get("match_name") or m.get("event_name") or "Sony LIV Live Stream"
                                valid_candidates.append((exp, url, title))
                except Exception:
                    continue
        except Exception:
            pass

        if valid_candidates:
            # Sort by expiration timestamp descending (freshest first)
            valid_candidates.sort(key=lambda x: x[0], reverse=True)
            best = valid_candidates[0]
            return best[1], best[2]
        return None

    async def sync(self) -> Dict[str, Any]:
        """Performs full synchronization, channel building, and disk persistence."""
        async with self.lock:
            data, source = await self.fetch_remote_json()
            if not data:
                # If unable to fetch, read existing channels.json from disk
                if self.static_channels_path.exists():
                    try:
                        with open(self.static_channels_path, "r", encoding="utf-8") as f:
                            self.cached_channels = json.load(f)
                    except Exception:
                        pass
                return {
                    "success": False,
                    "message": "Failed to fetch remote JSON, loaded local cache",
                    "total_channels": len(self.cached_channels),
                    "source": "fallback_disk"
                }

            self.last_sync_time = time.time()
            self.last_sync_source = source
            matches = data.get("matches", [])
            self.cached_matches = matches

            # Check if there is a live stream in m3u
            m3u_live = await self.fetch_remote_m3u_live_url()
            active_candidate_url = None
            active_candidate_title = None

            if m3u_live:
                cand_url, cand_title = m3u_live
                if self.is_token_valid(cand_url):
                    active_candidate_url = cand_url
                    active_candidate_title = cand_title

            # Check matches in json for isLive: true
            if not active_candidate_url:
                for m in matches:
                    if m.get("isLive") and (m.get("dai_url") or m.get("video_url")):
                        url = m.get("dai_url") or m.get("video_url")
                        if self.is_token_valid(url):
                            active_candidate_url = url
                            active_candidate_title = m.get("match_name") or m.get("event_name")
                            break

            # If not in current json, inspect recent git commits in local repo for an active valid token
            if not active_candidate_url:
                commit_stream = self.find_recent_valid_commit_stream()
                if commit_stream:
                    active_candidate_url, active_candidate_title = commit_stream

            # If still no active candidate, check if current active_live_stream is still valid
            if not active_candidate_url and self.active_live_stream and self.is_token_valid(self.active_live_stream):
                active_candidate_url = self.active_live_stream
                active_candidate_title = self.active_event_name

            # If still nothing or expired, fall back to STANDBY_STREAM_URL
            effective_stream_url = active_candidate_url or STANDBY_STREAM_URL
            self.active_live_stream = effective_stream_url
            self.active_event_name = active_candidate_title or "Sony LIV Sports Center (Standby)"
            self.token_expiry = self.parse_token_expiry(effective_stream_url)

            # Build channels catalog
            channels = []
            seen_ids = set()

            # 1. Add current live event if active
            if active_candidate_url and active_candidate_url != STANDBY_STREAM_URL:
                ch_id = "sonyliv.active_live"
                seen_ids.add(ch_id)
                channels.append({
                    "id": ch_id,
                    "name": f"🔴 LIVE NOW: {self.active_event_name}",
                    "raw_name": f"{self.active_event_name} [Sony Sports Live]",
                    "resolution": "1080P",
                    "logo": "https://origin-staticv2.sonyliv.com/videoasset_images/manage_file/1000027143/179275492633881_NZ_vs_IND_A_1st_test_day3_live_landscape_thumb.jpg",
                    "group": "Live Sports",
                    "url": active_candidate_url,
                    "category": "cricket",
                    "language": "English / Hindi",
                    "language_code": "eng",
                    "broadcast_channel": "Sony Sports Ten 5",
                    "is_live": True
                })

            # 2. Add all matches from JSON
            for idx, m in enumerate(matches):
                cid = str(m.get("contentId", f"match_{idx}"))
                lang_code = m.get("audioLanguageName", "HIN").upper()
                lang_name = LANG_MAP.get(lang_code, lang_code)
                channel_name = m.get("broadcast_channel", "Sony Sports Ten 5")
                raw_event = m.get("event_name", "Sony LIV Event")
                category = (m.get("event_category") or "Cricket").lower()
                clean_event = raw_event.replace("Upcoming - ", "").strip()

                is_live_flag = bool(m.get("isLive", False))
                match_stream_url = m.get("dai_url") or m.get("video_url")
                
                # Check if match has its own valid live URL, otherwise use effective active stream
                if match_stream_url and self.is_token_valid(match_stream_url):
                    stream_url = match_stream_url
                else:
                    stream_url = effective_stream_url

                ch_id = f"sonyliv.{cid}@{lang_code}"
                if ch_id in seen_ids:
                    ch_id = f"sonyliv.{cid}_{idx}@{lang_code}"
                seen_ids.add(ch_id)

                channels.append({
                    "id": ch_id,
                    "name": f"{channel_name}: {clean_event} ({lang_name})",
                    "raw_name": f"{raw_event} [{channel_name} - {lang_code}]",
                    "resolution": "1080P",
                    "logo": m.get("src", ""),
                    "group": m.get("event_category", "Cricket"),
                    "url": stream_url,
                    "category": category,
                    "language": lang_name,
                    "language_code": lang_code.lower(),
                    "broadcast_channel": channel_name,
                    "is_live": is_live_flag,
                    "content_id": cid
                })

            # 3. Add 24/7 flagship Sony Sports Ten network channels
            flagship = [
                ("SonySportsTen5.HD", "Sony Sports Ten 5 HD (Cricket & UEFA)", "cricket", "hin", "Sony Sports Ten 5"),
                ("SonySportsTen2.HD", "Sony Sports Ten 2 HD (ISL Football & Tennis)", "football", "hin", "Sony Sports Ten 2"),
                ("SonySportsTen1.HD", "Sony Sports Ten 1 HD (WWE & Combat Sports)", "sports", "eng", "Sony Sports Ten 1"),
                ("SonySportsTen3.HD", "Sony Sports Ten 3 HD (Hindi Sports Network)", "cricket", "hin", "Sony Sports Ten 3"),
            ]
            for fid, fname, fcat, flang, fbc in flagship:
                if fid not in seen_ids:
                    seen_ids.add(fid)
                    channels.insert(0, {
                        "id": fid,
                        "name": fname,
                        "raw_name": f"{fname} (1080p)",
                        "resolution": "1080P",
                        "logo": "https://origin-staticv2.sonyliv.com/videoasset_images/manage_file/1000027296/1792867384276495_coc_NZvsIND26_3rd_t20i_dated_landscape_thumb.jpg",
                        "group": "Flagship Network",
                        "url": effective_stream_url,
                        "category": fcat,
                        "language": "Hindi" if flang == "hin" else "English",
                        "language_code": flang,
                        "broadcast_channel": fbc,
                        "is_live": True
                    })

            self.cached_channels = channels

            # Save to disk
            try:
                self.static_channels_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.static_channels_path, "w", encoding="utf-8") as f:
                    json.dump(channels, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.info(f"Root static channels read-only ({e}), caching to /tmp/channels.json")
                try:
                    with open(Path("/tmp/channels.json"), "w", encoding="utf-8") as f:
                        json.dump(channels, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass

            return {
                "success": True,
                "source": self.last_sync_source,
                "total_channels": len(channels),
                "active_event": self.active_event_name,
                "active_stream_url": self.active_live_stream,
                "has_real_stream": (self.active_live_stream != STANDBY_STREAM_URL),
                "token_expiry": self.token_expiry,
                "synced_at": datetime.now(timezone.utc).isoformat()
            }

    def get_status(self) -> Dict[str, Any]:
        """Returns current synchronizer status."""
        seconds_left = None
        if self.token_expiry:
            seconds_left = max(0, int(self.token_expiry - time.time()))

        return {
            "status": "online",
            "last_sync_source": self.last_sync_source,
            "last_sync_time": self.last_sync_time,
            "total_channels": len(self.cached_channels),
            "active_event": self.active_event_name,
            "has_real_stream": (self.active_live_stream != STANDBY_STREAM_URL and self.active_live_stream is not None),
            "token_valid": self.is_token_valid(self.active_live_stream or ""),
            "token_expiry_timestamp": self.token_expiry,
            "token_seconds_left": seconds_left,
            "active_stream_url": self.active_live_stream or STANDBY_STREAM_URL
        }

# Global singleton
sync_manager = StreamSyncManager(BASE_DIR)
