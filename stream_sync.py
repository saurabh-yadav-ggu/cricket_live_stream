"""
StreamSync Module for StreamBox
Handles dynamic synchronization with external repository & local clone:
Sonyliv-Playlist-Autoupdate (https://github.com/sportlive18/Sonyliv-Playlist-Autoupdate.git)

Features:
- Full synchronization of 23 24/7 TV channels from sony.m3u (Entertainment, Sports, Movies, Kids, Infotainment)
- Real-time live sports match stream extraction from sonyliv.json & sonyliv.m3u
- Multiple fallback sources (sportlive18, saurabh-yadav-ggu, local Sonyliv-Playlist-Autoupdate clone)
- Akamai & CDN token expiration inspection and live probing
- Standby / slate stream fallback to prevent format errors
- Automatic catalog generation and persistence for static/channels.json
"""

import asyncio
import json
import logging
import os
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

# GitHub stream source endpoints (sportlive18/Sonyliv-Playlist-Autoupdate)
GITHUB_BASE_PRIMARY = "https://raw.githubusercontent.com/sportlive18/Sonyliv-Playlist-Autoupdate/main"
GITHUB_BASE_FALLBACK = "https://raw.githubusercontent.com/saurabh-yadav-ggu/Sonyliv-Playlist-Autoupdate/main"
GITHUB_LEGACY_FALLBACK = "https://raw.githubusercontent.com/sayanpal514-hue/SONYLIV-AUTO-UPDATED-PLAYLIST/main"

GITHUB_PRIMARY_JSON = f"{GITHUB_BASE_PRIMARY}/sonyliv.json"
GITHUB_PRIMARY_M3U = f"{GITHUB_BASE_PRIMARY}/sonyliv.m3u"
GITHUB_PRIMARY_SONY_M3U = f"{GITHUB_BASE_PRIMARY}/sony.m3u"
GITHUB_PRIMARY_JSON2 = f"{GITHUB_BASE_PRIMARY}/sonyliv2.json"
GITHUB_PRIMARY_M3U2 = f"{GITHUB_BASE_PRIMARY}/sonyliv2.m3u"

GITHUB_FALLBACK_JSON = f"{GITHUB_BASE_FALLBACK}/sonyliv.json"
GITHUB_FALLBACK_M3U = f"{GITHUB_BASE_FALLBACK}/sonyliv.m3u"
GITHUB_FALLBACK_SONY_M3U = f"{GITHUB_BASE_FALLBACK}/sony.m3u"

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
    "MAR": "Marathi",
}

# Curated high-resolution official channel logos for Sony LIV TV channels
CHANNEL_LOGOS = {
    "set-hd.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/SET_HD_logo.png/512px-SET_HD_logo.png",
    "sab-hd.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Sony_SAB_2022.svg/512px-Sony_SAB_2022.svg.png",
    "marathi.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Sony_Marathi_logo.png/512px-Sony_Marathi_logo.png",
    "pal.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Sony_Pal_logo.png/512px-Sony_Pal_logo.png",
    "aath.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Sony_Aath_logo.png/512px-Sony_Aath_logo.png",
    "yay.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Sony_YAY%21_logo.png/512px-Sony_YAY%21_logo.png",
    "max-hd.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Sony_Max_logo.png/512px-Sony_Max_logo.png",
    "max.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Sony_Max_logo.png/512px-Sony_Max_logo.png",
    "max2.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Sony_Max_2_logo.png/512px-Sony_Max_2_logo.png",
    "wah.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Sony_Wah_logo.png/512px-Sony_Wah_logo.png",
    "pix-hd.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Sony_PIX_logo.png/512px-Sony_PIX_logo.png",
    "ten1-hd.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Sony_Sports_Ten_1.svg/512px-Sony_Sports_Ten_1.svg.png",
    "ten1.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Sony_Sports_Ten_1.svg/512px-Sony_Sports_Ten_1.svg.png",
    "ten2-hd.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Sony_Sports_Ten_2.svg/512px-Sony_Sports_Ten_2.svg.png",
    "ten2.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Sony_Sports_Ten_2.svg/512px-Sony_Sports_Ten_2.svg.png",
    "ten3-hd.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Sony_Sports_Ten_3.svg/512px-Sony_Sports_Ten_3.svg.png",
    "ten3.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Sony_Sports_Ten_3.svg/512px-Sony_Sports_Ten_3.svg.png",
    "ten4-hd.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Sony_Sports_Ten_4.svg/512px-Sony_Sports_Ten_4.svg.png",
    "ten4.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Sony_Sports_Ten_4.svg/512px-Sony_Sports_Ten_4.svg.png",
    "ten4-kan.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Sony_Sports_Ten_4.svg/512px-Sony_Sports_Ten_4.svg.png",
    "ten5-hd.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Sony_Sports_Ten_5.svg/512px-Sony_Sports_Ten_5.svg.png",
    "ten5.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Sony_Sports_Ten_5.svg/512px-Sony_Sports_Ten_5.svg.png",
    "bbc-earth.sonyliv": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Sony_BBC_Earth.svg/512px-Sony_BBC_Earth.svg.png",
}


class StreamSyncManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.static_channels_path = base_dir / "static" / "channels.json"
        
        # Priority local repository folder
        if (base_dir / "Sonyliv-Playlist-Autoupdate").exists():
            self.local_repo_path = base_dir / "Sonyliv-Playlist-Autoupdate"
        else:
            self.local_repo_path = base_dir / "SONYLIV-AUTO-UPDATED-PLAYLIST"
        
        self.last_sync_time: Optional[float] = None
        self.last_sync_source: str = "none"
        self.cached_matches: List[Dict[str, Any]] = []
        self.cached_channels: List[Dict[str, Any]] = []
        self.active_live_stream: Optional[str] = None
        self.active_event_name: str = "Sony LIV Sports Center"
        self.token_expiry: Optional[int] = None
        self._lock: Optional[asyncio.Lock] = None

        # Synchronously load cached channels on instantiation for instant zero-latency cold starts
        self.load_cached_catalog_sync()

    def parse_token_expiry(self, url: str) -> Optional[int]:
        """Extracts exp=<timestamp> from Akamai / slivcdn signed URL."""
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
        return expiry > (time.time() + 60)

    def load_cached_catalog_sync(self):
        """Immediately loads channels from channels.json or local clone for zero-latency boot."""
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
                            if ch.get("is_live") and ch.get("url") and self.is_token_valid(ch["url"]):
                                self.active_live_stream = ch["url"]
                                self.active_event_name = ch.get("name", "Sony LIV Live Feed")
                                self.token_expiry = self.parse_token_expiry(ch["url"])
                                break
                        if not self.active_live_stream and len(data) > 0:
                            self.active_live_stream = data[0].get("url") or STANDBY_STREAM_URL
                            self.active_event_name = data[0].get("name", "Sony LIV Live Feed")
                        logger.info(f"Loaded {len(data)} channels from {p}")
                        return
                except Exception as exc:
                    logger.warning(f"Failed to load cached channels from {p}: {exc}")

        # Fallback: parse directly from local Sonyliv-Playlist-Autoupdate if static/channels.json missing
        self._build_catalog_from_local_files_sync()

    def _build_catalog_from_local_files_sync(self):
        """Fast fallback to build channels directly from local clone files."""
        sony_m3u_file = self.local_repo_path / "sony.m3u"
        json_file = self.local_repo_path / "sonyliv.json"
        
        m3u_text = ""
        if sony_m3u_file.exists():
            try:
                m3u_text = sony_m3u_file.read_text(encoding="utf-8")
            except Exception:
                pass

        json_data = {}
        if json_file.exists():
            try:
                json_data = json.loads(json_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        if m3u_text or json_data:
            channels, active_url, active_title = self._assemble_channel_catalog(m3u_text, json_data)
            if channels:
                self.cached_channels = channels
                self.active_live_stream = active_url or STANDBY_STREAM_URL
                self.active_event_name = active_title or "Sony LIV Live Stream"
                self.token_expiry = self.parse_token_expiry(self.active_live_stream)
                self.last_sync_source = "local_repo:boot"
                self.last_sync_time = time.time()

    @property
    def lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def probe_stream(self, url: str) -> bool:
        """Lightweight check to verify if the stream manifest responds with 200."""
        if not url:
            return False
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "https://www.sonyliv.com/",
            "Origin": "https://www.sonyliv.com",
            "Accept": "*/*"
        }
        try:
            async with httpx.AsyncClient(timeout=4.0, verify=False, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                return resp.status_code == 200 and ("#EXTM3U" in resp.text[:100])
        except Exception:
            return False

    def parse_sony_m3u(self, m3u_text: str) -> List[Dict[str, Any]]:
        """Parses all 23 TV broadcast channels from sony.m3u."""
        channels = []
        if not m3u_text:
            return channels

        lines = m3u_text.splitlines()
        current = {}
        for line in lines:
            line = line.strip()
            if line.startswith("#EXTINF"):
                m_id = re.search(r'tvg-id="([^"]+)"', line)
                m_name = re.search(r'tvg-name="([^"]+)"', line)
                m_group = re.search(r'group-title="([^"]+)"', line)
                m_logo = re.search(r'tvg-logo="([^"]+)"', line)
                
                raw_title = line.split(",")[-1].strip() if "," in line else "Sony LIV Channel"
                ch_id = m_id.group(1) if m_id else re.sub(r'[^a-zA-Z0-9]', '_', raw_title.lower())
                ch_name = m_name.group(1) if m_name else raw_title
                group = m_group.group(1) if m_group else "SonyLIV Network"
                logo = m_logo.group(1) if m_logo else CHANNEL_LOGOS.get(ch_id, "")

                # Determine Category
                grp_lower = group.lower()
                name_lower = ch_name.lower()
                if "entertainment" in grp_lower:
                    category = "entertainment"
                elif "kids" in grp_lower:
                    category = "kids"
                elif "movies" in grp_lower:
                    category = "movies"
                elif "sports" in grp_lower:
                    if "ten 3" in name_lower or "ten 5" in name_lower:
                        category = "cricket"
                    elif "ten 2" in name_lower:
                        category = "football"
                    else:
                        category = "sports"
                elif "infotainment" in grp_lower:
                    category = "infotainment"
                else:
                    category = "sports"

                # Determine Language
                if "marathi" in name_lower:
                    lang, lang_code = "Marathi", "mar"
                elif "aath" in name_lower:
                    lang, lang_code = "Bengali", "ben"
                elif "kannada" in name_lower:
                    lang, lang_code = "Kannada", "kan"
                elif "ten 4" in name_lower:
                    lang, lang_code = "Tamil / Telugu", "tam"
                elif any(k in name_lower for k in ["pix", "bbc", "ten 1", "ten 2"]):
                    lang, lang_code = "English", "eng"
                elif "ten 5" in name_lower:
                    lang, lang_code = "Hindi / English", "hin"
                else:
                    lang, lang_code = "Hindi", "hin"

                res = "1080P" if "hd" in name_lower else ("576P" if "sd" in name_lower else "720P")
                broadcast_channel = ch_name.replace(" HD", "").replace(" SD", "")

                current = {
                    "id": ch_id,
                    "name": ch_name,
                    "raw_name": f"{ch_name} ({res})",
                    "resolution": res,
                    "logo": logo or CHANNEL_LOGOS.get(ch_id, ""),
                    "group": group,
                    "category": category,
                    "language": lang,
                    "language_code": lang_code,
                    "broadcast_channel": broadcast_channel,
                    "is_live": True,
                }
            elif line.startswith("http") and current:
                current["url"] = line
                channels.append(current)
                current = {}

        return channels

    async def fetch_remote_data(self) -> Tuple[Optional[dict], Optional[str], str]:
        """
        Fetches sonyliv.json and sony.m3u from primary GitHub repository,
        fallback repository, or local Sonyliv-Playlist-Autoupdate directory.
        """
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            # 1. Primary repository (sportlive18/Sonyliv-Playlist-Autoupdate)
            try:
                rj = await client.get(GITHUB_PRIMARY_JSON, headers={"Cache-Control": "no-cache"})
                rm = await client.get(GITHUB_PRIMARY_SONY_M3U, headers={"Cache-Control": "no-cache"})
                if rj.status_code == 200:
                    json_data = rj.json()
                    m3u_text = rm.text if rm.status_code == 200 else ""
                    return json_data, m3u_text, "github:sportlive18"
            except Exception as e:
                logger.warning(f"Primary GitHub sportlive18 fetch failed: {e}")

            # 2. Fallback upstream (saurabh-yadav-ggu)
            try:
                rj = await client.get(GITHUB_FALLBACK_JSON, headers={"Cache-Control": "no-cache"})
                rm = await client.get(GITHUB_FALLBACK_SONY_M3U, headers={"Cache-Control": "no-cache"})
                if rj.status_code == 200:
                    json_data = rj.json()
                    m3u_text = rm.text if rm.status_code == 200 else ""
                    return json_data, m3u_text, "github:saurabh-yadav-ggu"
            except Exception as e:
                logger.warning(f"Fallback GitHub saurabh-yadav-ggu fetch failed: {e}")

        # 3. Local clone file system (Sonyliv-Playlist-Autoupdate)
        local_json = self.local_repo_path / "sonyliv.json"
        local_sony_m3u = self.local_repo_path / "sony.m3u"
        
        json_data = None
        m3u_text = ""

        if local_json.exists():
            try:
                with open(local_json, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
            except Exception as e:
                logger.warning(f"Local json read error: {e}")

        if local_sony_m3u.exists():
            try:
                with open(local_sony_m3u, "r", encoding="utf-8") as f:
                    m3u_text = f.read()
            except Exception as e:
                logger.warning(f"Local sony.m3u read error: {e}")

        if json_data or m3u_text:
            return json_data, m3u_text, "local_repo:Sonyliv-Playlist-Autoupdate"

        return None, None, "none"

    def _assemble_channel_catalog(
        self,
        m3u_text: str,
        json_data: Optional[dict]
    ) -> Tuple[List[Dict[str, Any]], Optional[str], Optional[str]]:
        """
        Combines 24/7 TV channels from sony.m3u with live sports events from sonyliv.json.
        Returns: (channels_list, active_live_stream_url, active_live_title)
        """
        channels: List[Dict[str, Any]] = []
        seen_ids = set()

        matches = (json_data or {}).get("matches", []) if isinstance(json_data, dict) else []
        self.cached_matches = matches

        # 1. Identify primary live match candidate
        active_candidate_url = None
        active_candidate_title = None
        active_candidate_logo = None

        for m in matches:
            if m.get("isLive") and (m.get("dai_url") or m.get("video_url")):
                url = m.get("dai_url") or m.get("video_url")
                if self.is_token_valid(url):
                    active_candidate_url = url
                    m_name = m.get("match_name") or ""
                    e_name = m.get("event_name") or ""
                    active_candidate_title = f"{m_name} - {e_name}" if (m_name and e_name) else (m_name or e_name or "Sony LIV Live Match")
                    active_candidate_logo = m.get("src")
                    # Prefer Hindi or English feed for hero player
                    if m.get("audioLanguageName") in ("HIN", "ENG"):
                        break

        # 2. Parse 23 24/7 TV channels from sony.m3u
        tv_channels = self.parse_sony_m3u(m3u_text)

        # If no active match URL yet, check if Sony Sports Ten 5 or Ten 1 has a valid stream
        if not active_candidate_url and tv_channels:
            for ch in tv_channels:
                if "ten 5" in ch["name"].lower() or "ten 1" in ch["name"].lower():
                    if self.is_token_valid(ch["url"]):
                        active_candidate_url = ch["url"]
                        active_candidate_title = f"{ch['name']} Live Broadcast"
                        break

        effective_stream_url = active_candidate_url or STANDBY_STREAM_URL
        effective_event_name = active_candidate_title or "Sony LIV Sports Center (Standby)"

        # 3. Add top Featured Live Event Banner Card
        if active_candidate_url and active_candidate_url != STANDBY_STREAM_URL:
            live_banner_id = "sonyliv.active_live"
            seen_ids.add(live_banner_id)
            channels.append({
                "id": live_banner_id,
                "name": f"🔴 LIVE NOW: {effective_event_name}",
                "raw_name": f"{effective_event_name} [Sony Sports Live]",
                "resolution": "1080P",
                "logo": active_candidate_logo or "https://origin-staticv2.sonyliv.com/videoasset_images/manage_file/1000027300/1792876687980737_NZvsIND_3rd_t20i_clean_landscape_thumb.jpg",
                "group": "Live Sports",
                "url": active_candidate_url,
                "category": "cricket",
                "language": "Hindi / English",
                "language_code": "hin",
                "broadcast_channel": "Sony Sports Ten 5",
                "is_live": True
            })

        # 4. Add Live Match Language Feeds from sonyliv.json
        for idx, m in enumerate(matches):
            if m.get("isLive"):
                cid = str(m.get("contentId", f"live_{idx}"))
                lang_code = (m.get("audioLanguageName") or "HIN").upper()
                lang_name = LANG_MAP.get(lang_code, lang_code)
                channel_name = m.get("broadcast_channel", "Sony Sports Ten 5")
                raw_event = m.get("event_name", "Sony LIV Event")
                match_name = m.get("match_name", "")
                category = (m.get("event_category") or "Cricket").lower()
                clean_event = raw_event.replace("Upcoming - ", "").strip()
                stream_url = m.get("dai_url") or m.get("video_url") or effective_stream_url

                ch_id = f"sonyliv.{cid}@{lang_code.lower()}"
                if ch_id in seen_ids:
                    ch_id = f"sonyliv.{cid}_{idx}@{lang_code.lower()}"
                seen_ids.add(ch_id)

                full_title = f"{channel_name}: {clean_event}"
                if match_name:
                    full_title += f" • {match_name}"
                else:
                    full_title += f" ({lang_name})"

                channels.append({
                    "id": ch_id,
                    "name": full_title,
                    "raw_name": f"{raw_event} [{channel_name} - {lang_code}]",
                    "resolution": "1080P",
                    "logo": m.get("src") or active_candidate_logo or "",
                    "group": m.get("event_category", "Cricket"),
                    "url": stream_url,
                    "category": category,
                    "language": lang_name,
                    "language_code": lang_code.lower(),
                    "broadcast_channel": channel_name,
                    "is_live": True,
                    "content_id": cid
                })

        # 5. Add 24/7 TV Channels from sony.m3u (SET HD, SAB HD, Ten 1-5, MAX, PIX, Yay, etc.)
        for ch in tv_channels:
            if ch["id"] not in seen_ids:
                seen_ids.add(ch["id"])
                channels.append(ch)

        # 6. Add Upcoming Matches from sonyliv.json
        for idx, m in enumerate(matches):
            if not m.get("isLive"):
                cid = str(m.get("contentId", f"upcoming_{idx}"))
                lang_code = (m.get("audioLanguageName") or "HIN").upper()
                lang_name = LANG_MAP.get(lang_code, lang_code)
                channel_name = m.get("broadcast_channel", "Sony Sports Network")
                raw_event = m.get("event_name", "Sony LIV Event")
                category = (m.get("event_category") or "Sports").lower()
                clean_event = raw_event.replace("Upcoming - ", "").strip()

                ch_id = f"sonyliv.upcoming.{cid}_{idx}@{lang_code.lower()}"
                if ch_id not in seen_ids:
                    seen_ids.add(ch_id)
                    channels.append({
                        "id": ch_id,
                        "name": f"Upcoming: {clean_event} ({lang_name})",
                        "raw_name": f"{raw_event} [{channel_name}]",
                        "resolution": "1080P",
                        "logo": m.get("src") or "",
                        "group": m.get("event_category", "Sports"),
                        "url": effective_stream_url,
                        "category": category,
                        "language": lang_name,
                        "language_code": lang_code.lower(),
                        "broadcast_channel": channel_name,
                        "is_live": False,
                        "content_id": cid
                    })

        return channels, active_candidate_url, active_candidate_title

    async def sync(self) -> Dict[str, Any]:
        """Performs full synchronization, channel building, and disk persistence."""
        async with self.lock:
            json_data, m3u_text, source = await self.fetch_remote_data()
            
            if not json_data and not m3u_text:
                # If unable to fetch, ensure disk cache is loaded
                if self.static_channels_path.exists():
                    try:
                        with open(self.static_channels_path, "r", encoding="utf-8") as f:
                            self.cached_channels = json.load(f)
                    except Exception:
                        pass
                return {
                    "success": False,
                    "message": "Failed to fetch remote source, retained local cache",
                    "total_channels": len(self.cached_channels),
                    "source": "fallback_disk"
                }

            self.last_sync_time = time.time()
            self.last_sync_source = source

            channels, active_candidate_url, active_candidate_title = self._assemble_channel_catalog(
                m3u_text or "", json_data
            )

            # If no active match was found, check if current active_live_stream is still valid
            if not active_candidate_url and self.active_live_stream and self.is_token_valid(self.active_live_stream):
                active_candidate_url = self.active_live_stream
                active_candidate_title = self.active_event_name

            effective_stream_url = active_candidate_url or STANDBY_STREAM_URL
            self.active_live_stream = effective_stream_url
            self.active_event_name = active_candidate_title or "Sony LIV Sports Center (Standby)"
            self.token_expiry = self.parse_token_expiry(effective_stream_url)
            self.cached_channels = channels

            # Save to disk (static/channels.json)
            try:
                self.static_channels_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.static_channels_path, "w", encoding="utf-8") as f:
                    json.dump(channels, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.info(f"Root static channels write error ({e}), writing to /tmp/channels.json")
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
