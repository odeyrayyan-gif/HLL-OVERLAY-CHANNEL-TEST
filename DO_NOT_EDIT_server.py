"""
HLL Overlay Local Server
Serves all HTML files and handles config read/write for the hub.
Run via start.bat — do not close the terminal window while streaming.
"""

import json, os, threading, socket, urllib.request, shutil, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# Always run from the folder this script lives in
# This ensures downloads and file reads go to the right place
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ── AUTO-UPDATER ──────────────────────────────────────────────────────────────
GITHUB_RAW   = "https://raw.githubusercontent.com/odeyrayyan-gif/HLL-OVERLAY-TEST/main/"
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
    "DO_NOT_EDIT_killstreaks.html",
    "DO_NOT_EDIT_killfeed.html",
    "DO_NOT_EDIT_tank_scoreboard.html",
    "DO_NOT_EDIT_melee_leaderboard.html",
    "DO_NOT_EDIT_message_banner.html",
    "changelog.md",
    "start.bat",
    "README.txt",
]

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
            self.send_json(self.read_config())
            return
        # ── /player — return current spotlight player name ──
        if path == "/player":
            name = self.read_player()
            self.send_json({"player": name})
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
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return {"api_endpoint": "", "api_logs_endpoint": "", "swap_sides": False, "player": "", "allied_faction": "ALLIES", "ticker_messages": [], "saved_servers": []}

    def write_config(self, data):
        existing = self.read_config()
        existing.update(data)
        with open(CONFIG_FILE, "w") as f:
            json.dump(existing, f, indent=2)

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
    check_for_updates()

    # Make sure config and player files exist
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"api_endpoint": "", "api_logs_endpoint": "", "swap_sides": False, "player": "", "allied_faction": "ALLIES", "ticker_messages": [], "saved_servers": []}, f, indent=2)
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
