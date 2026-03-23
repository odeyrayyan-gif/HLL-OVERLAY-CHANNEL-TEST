# HLL Command Hub Overlay

Local overlay system for Hell Let Loose streamers.  
This repo contains the web overlays, local server script, and Windows launch/install scripts.

## Quick start (Windows)

1. Clone the repo:
   ```powershell
   git clone https://github.com/odeyrayyan-gif/HLL-OVERLAY-CHANNEL-TEST.git
   cd HLL-OVERLAY-CHANNEL-TEST
   ```
2. Run:
   - `install.bat` for guided install on a target machine, or
   - `start.bat` to launch directly from the repo folder.
3. Open `http://localhost:3000` in your browser.

## Main files

- `DO_NOT_EDIT_server.py` - local Python server that serves overlays and API data.
- `DO_NOT_EDIT_hub.html` - command/control hub UI.
- `DO_NOT_EDIT_*.html` - overlay pages for OBS browser sources.
- `DO_NOT_EDIT_settings.json` - saved local settings.
- `start.bat` - local launcher.
- `install.bat` - installer/updater script.
- `README.txt` - full end-user instructions.

## Notes

- This project is currently Windows-first (`.bat` scripts included).
- Keep filenames as-is unless you also update script references.
