"""
HLL Overlay Local Server
Serves all HTML files and handles config read/write for the hub.
Run via start.bat — do not close the terminal window while streaming.
"""

import json, os, threading, socket, urllib.request, shutil, sys, re, time
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# Always run from the folder this script lives in
# This ensures downloads and file reads go to the right place
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ── AUTO-UPDATER ──────────────────────────────────────────────────────────────
GITHUB_RAW   = "https://raw.githubusercontent.com/odeyrayyan-gif/HLL-OVERLAY/main/"
VERSION_FILE = "version.txt"

UPDATABLE_FILES = [
    "DO_NOT_EDIT_server.py",
    "DO_NOT_EDIT_hub.html",
    "DO_NOT_EDIT_team_compare.html",
    "DO_NOT_EDIT_map_overlay.html",
    "DO_NOT_EDIT_at_leaderboard.html",
    "DO_NOT_EDIT_player_spotlight.html",
    "DO_NOT_EDIT_top5_scroll_banner.html",
    "DO_NOT_EDIT_top10_scroll_banner.html",
    "DO_NOT_EDIT_top10_scoreboard.html",
    "DO_NOT_EDIT_killstreaks.html",
    "DO_NOT_EDIT_killfeed.html",
    "DO_NOT_EDIT_tank_scoreboard.html",
    "DO_NOT_EDIT_melee_leaderboard.html",
    "DO_NOT_EDIT_message_banner.html",
    "changelog.md",
    "start.bat",
    "README.txt",
]

# ── Counter namespace — unique to this overlay ──
COUNTER_NS = "hll-overlay-odey"

def ping_counter(key):
    """Fire-and-forget hit to countapi.xyz. Never blocks or crashes server."""
    try:
        import threading
        def _ping():
            try:
                url = f"https://api.countapi.xyz/hit/{COUNTER_NS}/{key}"
                urllib.request.urlopen(url, timeout=4)
            except Exception:
                pass  # Silent — counter is optional, never interrupts server
        threading.Thread(target=_ping, daemon=True).start()
    except Exception:
        pass

def get_local_version():
    try:
        with open(VERSION_FILE, "r") as f:
            return f.read().strip().strip("\n").strip()
    except:
        return "0.0.0"

def get_remote_version():
    try:
        url = GITHUB_RAW + VERSION_FILE + "?t=" + str(os.times()[4])
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.read().decode().strip().strip("\n").strip()
    except:
        return None

def download_file(filename):
    url = GITHUB_RAW + filename
    tmp = filename + ".tmp"
    try:
        urllib.request.urlretrieve(url, tmp)
        shutil.move(tmp, filename)
        return True
    except Exception as e:
        if os.path.exists(tmp):
            os.remove(tmp)
        print(f"  [!] Failed to download {filename}: {e}")
        return False

def check_for_updates():
    print("  Checking for updates...")
    local   = get_local_version()
    remote  = get_remote_version()

    if remote is None:
        print("  Could not reach update server — skipping update check.")
        return False

    # Debug — show exact bytes so any whitespace issues are visible
    print(f"  Local  version: [{local}] ({len(local)} chars)")
    print(f"  Remote version: [{remote}] ({len(remote)} chars)")

    if remote == local:
        print(f"  Up to date (v{local})")
        return False

    print(f"  Update available! v{local} → v{remote}")
    print("  Downloading updates...")
    success = []
    failed  = []
    for fname in UPDATABLE_FILES:
        if download_file(fname):
            success.append(fname)
        else:
            failed.append(fname)

    # Update local version file
    with open(VERSION_FILE, "w") as f:
        f.write(remote)

    if success:
        ping_counter("updates")  # count each update event
    print(f"  Updated {len(success)} files.")
    if failed:
        print(f"  Failed: {', '.join(failed)}")

    # Show changelog for the new version only
    try:
        changelog_url = GITHUB_RAW + "changelog.md?t=" + str(os.times()[4])
        with urllib.request.urlopen(changelog_url, timeout=5) as r:
            changelog = r.read().decode()

        # Extract only the section for the new version
        lines = changelog.split("\n")
        capture = False
        section = []
        for line in lines:
            if line.strip() == f"## v{remote}":
                capture = True
                continue
            if capture:
                # Stop at the next version header
                if line.startswith("## v"):
                    break
                section.append(line)

        print()
        print(f"  ── WHAT'S NEW IN v{remote} " + "─" * 30)
        if section:
            for line in section:
                if line.strip():
                    print(f"  {line}")
        else:
            print(f"  See changelog.md for full details.")
        print("  " + "─" * 54)
    except:
        pass

    print()
    print("  *** UPDATE COMPLETE — Please close and reopen start.bat ***")
    print()
    input("  Press Enter to exit...")
    raise SystemExit(0)

# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

CONFIG_FILE  = "DO_NOT_EDIT_settings.json"
PLAYER_FILE  = "DO_NOT_EDIT_player.txt"
PORT         = 3000

ANTI_TRIGGER_LIMITATION = (
    "Server logs cannot see crosshair position or on-screen visibility. "
    "This report only ranks server-observable timing/stat patterns for human review."
)

KILLER_KEYS = ("killer", "attacker", "player", "player_name", "player1", "by", "source")
VICTIM_KEYS = ("victim", "target", "killed", "player2", "against", "destination")
WEAPON_KEYS = ("weapon", "weapon_name", "gun", "loadout", "method")
TIME_KEYS = ("timestamp", "time", "date", "created", "created_at", "event_time")
LOG_LIST_KEYS = ("logs", "events", "records", "items", "data", "entries")

KILL_TEXT_PATTERNS = (
    re.compile(r"^(?P<killer>.+?)\s+killed\s+(?P<victim>.+?)(?:\s+with\s+(?P<weapon>.+))?$", re.I),
    re.compile(r"^(?P<victim>.+?)\s+was\s+killed\s+by\s+(?P<killer>.+?)(?:\s+with\s+(?P<weapon>.+))?$", re.I),
)

ANTI_TRIGGER_SAMPLE_EVENTS = [
    {"timestamp": 1000.0, "killer": "SyntheticSnap", "victim": "Alpha01", "weapon": "Rifle"},
    {"timestamp": 1000.42, "killer": "SyntheticSnap", "victim": "Alpha02", "weapon": "Rifle"},
    {"timestamp": 1000.88, "killer": "SyntheticSnap", "victim": "Alpha03", "weapon": "Rifle"},
    {"timestamp": 1001.31, "killer": "SyntheticSnap", "victim": "Alpha04", "weapon": "Rifle"},
    {"timestamp": 1001.76, "killer": "SyntheticSnap", "victim": "Alpha05", "weapon": "Rifle"},
    {"timestamp": 1002.23, "killer": "SyntheticSnap", "victim": "Alpha06", "weapon": "Rifle"},
    {"timestamp": 1002.71, "killer": "SyntheticSnap", "victim": "Alpha07", "weapon": "Rifle"},
    {"timestamp": 1003.19, "killer": "SyntheticSnap", "victim": "Alpha08", "weapon": "Rifle"},
    {"timestamp": 1012.0, "killer": "RegularPlayer", "victim": "Bravo01", "weapon": "SMG"},
    {"timestamp": 1050.0, "killer": "RegularPlayer", "victim": "Bravo02", "weapon": "SMG"},
    {"timestamp": 1105.0, "killer": "RegularPlayer", "victim": "Bravo03", "weapon": "Grenade"},
]

ANTI_TRIGGER_SAMPLE_STATS = {
    "result": {
        "stats": [
            {"player": "SyntheticSnap", "kills": 31, "deaths": 2, "weapons": {"Rifle": 29, "Grenade": 2}},
            {"player": "RegularPlayer", "kills": 9, "deaths": 8, "weapons": {"SMG": 6, "Grenade": 3}},
        ]
    }
}

def _first_value(item, keys):
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None

def _to_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default

def _parse_timestamp(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        ts = float(value)
        if ts > 1000000000000:
            return ts / 1000.0
        return ts
    text = str(value).strip()
    if not text:
        return None
    try:
        return _parse_timestamp(float(text))
    except ValueError:
        pass
    normalized = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).timestamp()
    except ValueError:
        pass
    match = re.search(r"\b(?P<h>\d{1,2}):(?P<m>\d{2})(?::(?P<s>\d{2}))?\b", text)
    if match:
        hours = int(match.group("h"))
        minutes = int(match.group("m"))
        seconds = int(match.group("s") or 0)
        return float(hours * 3600 + minutes * 60 + seconds)
    return None

def _extract_list(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in LOG_LIST_KEYS:
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nested = _extract_list(value)
            if nested:
                return nested
    result = payload.get("result")
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return _extract_list(result)
    return []

def extract_player_stats(payload):
    if isinstance(payload, dict):
        result = payload.get("result")
        if isinstance(result, dict) and isinstance(result.get("stats"), list):
            return result.get("stats")
        if isinstance(payload.get("stats"), list):
            return payload.get("stats")
        if isinstance(payload.get("players"), list):
            return payload.get("players")
    if isinstance(payload, list):
        return payload
    return []

def _parse_kill_text(text, default_time=None):
    clean = str(text or "").strip()
    for pattern in KILL_TEXT_PATTERNS:
        match = pattern.search(clean)
        if match:
            return {
                "timestamp": default_time,
                "killer": match.group("killer").strip(),
                "victim": match.group("victim").strip(),
                "weapon": (match.groupdict().get("weapon") or "Unknown").strip(),
            }
    return None

def extract_kill_events(payload):
    events = []
    for item in _extract_list(payload):
        if isinstance(item, str):
            parsed = _parse_kill_text(item)
            if parsed:
                events.append(parsed)
            continue
        if not isinstance(item, dict):
            continue

        default_time = _parse_timestamp(_first_value(item, TIME_KEYS))
        killer = _first_value(item, KILLER_KEYS)
        victim = _first_value(item, VICTIM_KEYS)
        weapon = _first_value(item, WEAPON_KEYS) or "Unknown"
        message = item.get("message") or item.get("msg") or item.get("text") or item.get("raw")
        action_text = " ".join(
            str(item.get(key, "")) for key in ("type", "action", "category", "event", "verb")
        ).lower()
        is_kill_event = (
            "kill" in action_text
            or (message and "kill" in str(message).lower())
            or (killer and victim)
        )
        if not is_kill_event:
            continue

        if killer and victim and str(killer) != str(victim):
            events.append({
                "timestamp": default_time,
                "killer": str(killer).strip(),
                "victim": str(victim).strip(),
                "weapon": str(weapon).strip() or "Unknown",
            })
            continue

        parsed = _parse_kill_text(message, default_time)
        if parsed and parsed["killer"] != parsed["victim"]:
            events.append(parsed)

    return sorted(events, key=lambda e: (e.get("timestamp") is None, e.get("timestamp") or 0))

def _weapon_summary(weapons):
    if not isinstance(weapons, dict) or not weapons:
        return {"top_weapon": "Unknown", "top_weapon_kills": 0, "top_weapon_ratio": 0.0}
    pairs = sorted(((str(k), _to_int(v)) for k, v in weapons.items()), key=lambda x: x[1], reverse=True)
    total = sum(count for _, count in pairs)
    if not pairs or total <= 0:
        return {"top_weapon": "Unknown", "top_weapon_kills": 0, "top_weapon_ratio": 0.0}
    return {
        "top_weapon": pairs[0][0],
        "top_weapon_kills": pairs[0][1],
        "top_weapon_ratio": round(pairs[0][1] / total, 3),
    }

def _max_events_in_window(timestamps, window_seconds):
    best = 0
    start = 0
    for end, ts in enumerate(timestamps):
        while ts - timestamps[start] > window_seconds:
            start += 1
        best = max(best, end - start + 1)
    return best

def _median(values):
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0

def _score_stats_only(player):
    kills = _to_int(player.get("kills"))
    deaths = _to_int(player.get("deaths"))
    weapons = _weapon_summary(player.get("weapons"))
    score = 0
    reasons = []
    if kills >= 40 and deaths <= 4:
        score += 18
        reasons.append(f"high aggregate K/D signal ({kills} kills, {deaths} deaths)")
    if kills >= 30 and weapons["top_weapon_ratio"] >= 0.85:
        score += 12
        reasons.append(f"{int(weapons['top_weapon_ratio'] * 100)}% of weapon kills from {weapons['top_weapon']}")
    return score, reasons, weapons

def build_anti_trigger_report(stats_payload=None, kill_events=None, source="live"):
    stats = extract_player_stats(stats_payload or {})
    events = kill_events or []
    by_player = {}

    for player in stats:
        if not isinstance(player, dict):
            continue
        name = player.get("player") or player.get("name")
        if not name:
            continue
        score, reasons, weapons = _score_stats_only(player)
        by_player[str(name)] = {
            "player": str(name),
            "score": score,
            "confidence": "low" if reasons else "info",
            "recommendation": "manual_review" if score >= 25 else "insufficient_data",
            "reasons": reasons,
            "metrics": {
                "kills": _to_int(player.get("kills")),
                "deaths": _to_int(player.get("deaths")),
                **weapons,
            },
        }

    grouped = {}
    for event in events:
        killer = str(event.get("killer") or "").strip()
        if not killer:
            continue
        grouped.setdefault(killer, []).append(event)

    for killer, player_events in grouped.items():
        timestamps = [
            _parse_timestamp(event.get("timestamp")) for event in player_events
            if _parse_timestamp(event.get("timestamp")) is not None
        ]
        timestamps.sort()
        intervals = [
            timestamps[i] - timestamps[i - 1]
            for i in range(1, len(timestamps))
            if timestamps[i] >= timestamps[i - 1]
        ]
        rapid_pairs = sum(1 for interval in intervals if interval <= 1.25)
        very_fast_pairs = sum(1 for interval in intervals if interval <= 0.35)
        rapid_rate = rapid_pairs / len(intervals) if intervals else 0.0
        median_interval = _median(intervals)
        max_5s = _max_events_in_window(timestamps, 5.0) if timestamps else 0
        max_10s = _max_events_in_window(timestamps, 10.0) if timestamps else 0

        weapon_counts = {}
        for event in player_events:
            weapon = str(event.get("weapon") or "Unknown")
            weapon_counts[weapon] = weapon_counts.get(weapon, 0) + 1
        weapons = _weapon_summary(weapon_counts)

        current = by_player.setdefault(killer, {
            "player": killer,
            "score": 0,
            "confidence": "info",
            "recommendation": "insufficient_data",
            "reasons": [],
            "metrics": {},
        })
        score = current["score"]
        reasons = list(current["reasons"])

        if len(timestamps) >= 6 and median_interval is not None and median_interval <= 1.25:
            score += 30
            reasons.append(f"median logged kill interval is {median_interval:.2f}s across {len(timestamps)} timed kills")
        if rapid_pairs >= 5 and rapid_rate >= 0.55:
            score += 25
            reasons.append(f"{rapid_pairs} of {len(intervals)} consecutive logged kills occurred within 1.25s")
        if very_fast_pairs >= 3:
            score += 15
            reasons.append(f"{very_fast_pairs} consecutive logged kills occurred within 0.35s")
        if max_5s >= 5:
            score += 18
            reasons.append(f"{max_5s} logged kills landed within a 5s window")
        elif max_10s >= 6:
            score += 10
            reasons.append(f"{max_10s} logged kills landed within a 10s window")
        if len(player_events) >= 8 and weapons["top_weapon_ratio"] >= 0.85:
            score += 10
            reasons.append(f"logged kills are concentrated on {weapons['top_weapon']} ({int(weapons['top_weapon_ratio'] * 100)}%)")

        if score >= 70:
            recommendation = "manual_review_high_priority"
            confidence = "high" if len(timestamps) >= 8 else "medium"
        elif score >= 45:
            recommendation = "manual_review"
            confidence = "medium"
        elif score >= 25:
            recommendation = "watchlist"
            confidence = "low"
        else:
            recommendation = "insufficient_data"
            confidence = "info"

        current.update({
            "score": min(score, 100),
            "confidence": confidence,
            "recommendation": recommendation,
            "reasons": reasons,
            "metrics": {
                **current.get("metrics", {}),
                "logged_kills": len(player_events),
                "timed_logged_kills": len(timestamps),
                "rapid_pairs_1_25s": rapid_pairs,
                "very_fast_pairs_0_35s": very_fast_pairs,
                "rapid_pair_rate": round(rapid_rate, 3),
                "median_interval_seconds": round(median_interval, 3) if median_interval is not None else None,
                "max_kills_5s": max_5s,
                "max_kills_10s": max_10s,
                "logged_top_weapon": weapons["top_weapon"],
                "logged_top_weapon_ratio": weapons["top_weapon_ratio"],
            },
        })

    candidates = sorted(
        (candidate for candidate in by_player.values() if candidate["score"] > 0),
        key=lambda item: (-item["score"], item["player"].lower())
    )
    return {
        "ok": True,
        "source": source,
        "generated_at": int(time.time()),
        "summary": {
            "players_analyzed": len(by_player),
            "kill_events_analyzed": len(events),
            "limitation": ANTI_TRIGGER_LIMITATION,
        },
        "candidates": candidates,
        "notes": [
            "Use as triage only; do not ban solely from this report.",
            "For stronger signals, configure api_logs_endpoint so the report can use kill timing instead of aggregate stats only.",
        ],
    }

class HLLHandler(SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        # Suppress noisy request logs — only print errors
        if args[1] not in ('200', '304'):
            print(f"  [{args[1]}] {args[0]}")

    def handle_error(self, request, client_address):
        # Ignore connection resets — phone screen locks, tab closes mid-request etc.
        import sys
        err = sys.exc_info()[1]
        if isinstance(err, (ConnectionResetError, BrokenPipeError, ConnectionAbortedError)):
            return  # Normal — ignore cleanly
        # Also ignore Windows-specific socket errors (WinError 10053, 10054)
        if isinstance(err, OSError) and hasattr(err, 'winerror') and err.winerror in (10053, 10054):
            return
        # For anything else, print it so real bugs are visible
        print(f"  [!] Unexpected error from {client_address}: {err}")

    def do_GET(self):
        # Strip query string for routing
        path = self.path.split("?")[0]
        # ── / — redirect to hub ──
        if path == "/" or path == "":
            self.send_response(302)
            self.send_header("Location", "/DO_NOT_EDIT_hub.html")
            self.send_cors_headers()
            self.end_headers()
            return
        # ── /favicon.ico — return empty so browser stops asking ──
        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        # ── Legacy filename redirects — old OBS sources still work ──
        LEGACY = {
            "/killstreaks.html":                  "/DO_NOT_EDIT_killstreaks.html",
            "/compare.html":                      "/DO_NOT_EDIT_team_compare.html",
            "/map_team_info_with_deaths.html":    "/DO_NOT_EDIT_map_overlay.html",
            "/player_spotlight.html":             "/DO_NOT_EDIT_player_spotlight.html",
            "/top_rocket_kills.html":             "/DO_NOT_EDIT_at_leaderboard.html",
            "/top5.html":                         "/DO_NOT_EDIT_top5_scroll_banner.html",
            "/top10.html":                        "/DO_NOT_EDIT_top10_scroll_banner.html",
            "/DO_NOT_EDIT_bottom_ticker.html":    "/DO_NOT_EDIT_top5_scroll_banner.html",
            "/team_compare.html":                 "/DO_NOT_EDIT_team_compare.html",
            "/map.html":                          "/DO_NOT_EDIT_map_overlay.html",
            "/rockets.html":                      "/DO_NOT_EDIT_at_leaderboard.html",
            "/spotlight.html":                    "/DO_NOT_EDIT_player_spotlight.html",
            "/kills.html":                        "/DO_NOT_EDIT_killstreaks.html",
            "/killfeed.html":                     "/DO_NOT_EDIT_killfeed.html",
            "/tank_scoreboard.html":              "/DO_NOT_EDIT_tank_scoreboard.html",
            "/melee_leaderboard.html":            "/DO_NOT_EDIT_melee_leaderboard.html",
            "/message_banner.html":               "/DO_NOT_EDIT_message_banner.html",
        }
        if path in LEGACY:
            self.send_response(302)
            self.send_header("Location", LEGACY[path])
            self.send_cors_headers()
            self.end_headers()
            return
        # ── /config — return current settings as JSON ──
        if path == "/config":
            cfg = self.read_config()
            cfg["player"] = self.read_player()
            self.send_json(cfg)
            return
        # ── /player — return current spotlight player name ──
        if path == "/player":
            name = self.read_player()
            self.send_json({"player": name})
            return
        # ── /gamestate — proxy get_gamestate from CRCON ──
        if path == "/gamestate":
            try:
                cfg = self.read_config()
                endpoint = cfg.get("api_endpoint", "")
                if not endpoint:
                    self.send_json({"result": None})
                    return
                from urllib.parse import urlparse
                base_url = "{0.scheme}://{0.netloc}".format(urlparse(endpoint))
                url = base_url + "/api/get_gamestate?t=" + str(os.times()[4])
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read().decode())
                self.send_json(data)
            except Exception as e:
                self.send_json({"result": None, "error": str(e)})
            return

        # ── /teamview — proxy get_team_view from CRCON ──
        if path == "/teamview":
            try:
                cfg = self.read_config()
                endpoint = cfg.get("api_endpoint", "")
                if not endpoint:
                    self.send_json({"result": None})
                    return
                from urllib.parse import urlparse
                base_url = "{0.scheme}://{0.netloc}".format(urlparse(endpoint))
                url = base_url + "/api/get_team_view?t=" + str(os.times()[4])
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read().decode())
                self.send_json(data)
            except Exception as e:
                self.send_json({"result": None, "error": str(e)})
            return

        # ── /players — proxy live player list from CRCON to avoid CORS ──
        if path == "/players":
            try:
                cfg = self.read_config()
                endpoint = cfg.get("api_endpoint", "")
                if not endpoint:
                    self.send_json({"players": []})
                    return
                sep = "&" if "?" in endpoint else "?"
                url = endpoint + sep + "t=" + str(os.times()[4])
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    data = json.loads(r.read().decode())
                stats = data.get("result", {}).get("stats", [])
                self.send_json({"players": stats})
            except Exception as e:
                self.send_json({"players": []})
            return

        # ── /stats — proxy full CRCON stats response for overlays ──
        if path == "/stats":
            try:
                cfg = self.read_config()
                endpoint = cfg.get("api_endpoint", "")
                if not endpoint:
                    self.send_json({"result": None})
                    return
                sep = "&" if "?" in endpoint else "?"
                url = endpoint + sep + "t=" + str(os.times()[4])
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read().decode())
                self.send_json(data)
            except Exception as e:
                self.send_json({"result": None, "error": str(e)})
            return
        # ── Serve static files normally ──
        # Add no-cache headers for HTML files so updates show immediately
        if path.endswith('.html'):
            self.send_response(200)
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_cors_headers()
            try:
                with open(path.lstrip('/'), 'rb') as f:
                    content = f.read()
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            except:
                super().do_GET()
            return
        super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        # ── /config — save new settings ──
        if self.path == "/config":
            try:
                data = json.loads(body)
                self.write_config(data)
                self.send_json({"ok": True})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 400)
            return

        # ── /player — save spotlight player name ──
        if self.path == "/player":
            try:
                data = json.loads(body)
                name = data.get("player", "")
                self.write_player(name)
                self.send_json({"ok": True})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 400)
            return

        self.send_error(404)

    def do_OPTIONS(self):
        # Allow CORS for all origins (needed for OBS browser source)
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    # ── Helpers ──

    def send_json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def read_config(self):
        # Retry up to 3 times to handle race conditions during writes
        for attempt in range(3):
            try:
                with open(CONFIG_FILE, "r") as f:
                    content = f.read().strip()
                if not content:
                    import time; time.sleep(0.05)
                    continue
                data = json.loads(content)
                # Only return if we got a valid config with expected fields
                if isinstance(data, dict):
                    return data
            except (json.JSONDecodeError, IOError):
                import time; time.sleep(0.05)
        return {"api_endpoint": "", "api_logs_endpoint": "", "swap_sides": False, "player": "", "allied_faction": "ALLIES", "ticker_messages": [], "saved_servers": [], "top5_freq": "indefinite", "top10_freq": "indefinite", "stat_mode": "combat", "banner_stat_mode": "combat"}

    def write_config(self, data):
        existing = self.read_config()
        existing.update(data)
        # Atomic write — write to temp file then rename to avoid partial reads
        tmp = CONFIG_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(existing, f, indent=2)
        import os
        os.replace(tmp, CONFIG_FILE)

    def read_player(self):
        try:
            with open(PLAYER_FILE, "r") as f:
                return f.read().strip()
        except:
            return ""

    def write_player(self, name):
        with open(PLAYER_FILE, "w") as f:
            f.write(name)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


if __name__ == "__main__":
    # ── Check for updates before starting ──
    ping_counter("starts")   # count every server start
    check_for_updates()

    # Make sure config and player files exist
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"api_endpoint": "", "api_logs_endpoint": "", "swap_sides": False, "player": "", "allied_faction": "ALLIES", "ticker_messages": [], "saved_servers": [], "top5_freq": "indefinite", "top10_freq": "indefinite", "stat_mode": "combat", "banner_stat_mode": "combat"}, f, indent=2)
    if not os.path.exists(PLAYER_FILE):
        with open(PLAYER_FILE, "w") as f:
            f.write("")

    ip = get_local_ip()
    try:
        server = ThreadingHTTPServer(("", PORT), HLLHandler)
        server.allow_reuse_address = True
    except OSError:
        print(f"  [!] Port {PORT} is already in use.")
        print(f"  [!] Another instance may already be running.")
        print(f"  [!] Check your taskbar or close any existing terminal windows.")
        print()
        input("  Press Enter to exit...")
        raise SystemExit(1)

    print("=" * 55)
    print("  HLL OVERLAY SERVER — RUNNING")
    print("=" * 55)
    print(f"  Hub (this PC):  http://localhost:{PORT}")
    print(f"  Hub (phone):    http://{ip}:{PORT}")
    print(f"  OBS sources:    http://localhost:{PORT}/DO_NOT_EDIT_team_compare.html  etc.")
    print("=" * 55)
    print("  All overlays synced via local server.")
    print("  Keep this window open while streaming.")
    print("  Press Ctrl+C to stop.\n")

    server.serve_forever()
