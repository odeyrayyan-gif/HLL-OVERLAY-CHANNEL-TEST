================================================================
  HLL COMMAND HUB — README
  Hell Let Loose Live Overlay System
================================================================

WHAT IS THIS?
-------------
A local overlay system for Hell Let Loose streamers.
It runs a small server on your PC that feeds live game
stats to your OBS browser sources in real time.

You control everything from a web hub — on your PC browser
or from your phone on the same WiFi network.


================================================================
  REQUIREMENTS
================================================================

- Windows PC
- Python 3.x installed (see STEP 1 below)
- Hell Let Loose server with the CRCON web panel
- OBS Studio


================================================================
  STEP 1 — CHECK IF PYTHON IS ALREADY INSTALLED
================================================================

Windows does NOT come with Python pre-installed.
But you might already have it from other software.
Here is how to check in 30 seconds:

  1. Hold the Windows key and press R on your keyboard
  2. A small box appears — type:   cmd   and press Enter
  3. A black window opens — type:   python --version
     then press Enter

  YOU SEE "Python 3.x.x"
  Great! Python is installed. Skip to INSTALLING section.

  YOU SEE "Python was not found..." or an error
  Python is not installed. Follow INSTALLING PYTHON below.

  THE MICROSOFT STORE OPENS
  That is not real Python. Close it.
  Follow INSTALLING PYTHON below.


  ── INSTALLING PYTHON ────────────────────────────────────

  1. Go to this link in your browser:
     https://www.python.org/ftp/python/3.14.3/python-3.14.3-amd64.exe
     It will start downloading immediately

  2. Run the file that downloaded

  3. THE MOST IMPORTANT STEP:
     On the very first screen of the installer you will see
     a small checkbox at the bottom that says:
         "Add Python to PATH"
     TICK THAT BOX before clicking anything else.
     If you skip this, nothing will work and you will need
     to uninstall and reinstall Python.

  4. Click "Install Now"

  5. Wait for it to finish then close the installer

  6. To confirm it worked:
     Open cmd again (Windows + R, type cmd, press Enter)
     Type:   python --version   and press Enter
     You should see "Python 3.14.3"

  You only ever need to do this once.


================================================================
  STEP 2 — FINDING YOUR API URL
================================================================

This is the web link that connects the overlays to your
live game data. You find it once, paste it in, and never
need to find it again.

  BEFORE YOU START:
  Your CRCON web panel must be open in Google Chrome.
  CRCON is the community-made web tool for managing your
  HLL server. If you do not have it, ask your server admin.

  ── HOW TO FIND IT — STEP BY STEP ───────────────────────

  1. Open your CRCON scoreboard/stats link in Google Chrome
    

  2. Click on the tab at the top of the page that shows "current game"
    

  3. Press F12 on your keyboard
     A panel opens on the right side of your screen
     This is Chrome's built-in developer tools
     It looks scary but you only need one tab inside it

  4. Click the tab that says "Network" at the top of
     the developer panel
     You will see a list of requests, or it may be empty

  5. Press F5 to refresh the CRCON page
     You will see lots of entries appear in the list
     This is Chrome showing you every request the page made

  6. At the top of the Network panel there is a filter box
     Click it and type exactly:
         get_live_game_stats
     The long list shrinks down to just one or two items

  7. Click on the item that appears

  8. A smaller panel opens to the right
     Scroll up until you see a line that says:
         Request URL:
     Next to it is a web address that looks like:
         http://123.45.67.89:8010/api/get_live_game_stats
     The numbers will be different for your server

  9. Copy that entire address
     You can right-click it and choose Copy
     Or click it, select all, and press Ctrl+C

  10. You now have your API URL. Hold onto it for Step 3.

  ── COMMON QUESTIONS ────────────────────────────────────

  NOTHING SHOWS IN THE LIST AFTER FILTERING?
  Make sure you pressed F5 to refresh the page AFTER
  opening the Network tab. The tab needs to be open
  when the page loads to capture the requests.

  THE URL HAS EXTRA CHARACTERS AT THE END?
  For example: ?with_stats=true&something=else
  That is fine. You can copy the whole URL including
  the question mark and everything after it. Or you can
  stop copying at get_live_game_stats. Either works.

  I CANNOT FIND THE CRCON STATS PAGE?
  Try other pages in CRCON — look for "Live", "Scoreboard",
  "Stats", or "Players". Any page that shows a list of
  players with kills should trigger the request.


================================================================
  STEP 3 — FIRST TIME SETUP
================================================================

  1. Extract the HLL-Overlay folder anywhere on your PC
     Desktop or Documents works fine

  2. Double-click start.bat
     A black terminal window opens. This system receives
     regular updates — when a new version is available it
     will download automatically before the server starts.
     You may see:
         Checking for updates...
         Update available! v1.0.x -> v1.0.x
         Downloading updates...
         *** UPDATE COMPLETE — Please close and reopen start.bat ***
     If this happens, close the window and double-click
     start.bat again. The update only takes a few seconds.

     When no update is available you will see:
         HLL OVERLAY SERVER — RUNNING
         Hub (this PC):  http://localhost:3000
         Hub (phone):    http://192.168.x.x:3000
     Keep this window open the entire time you are streaming
     Closing it shuts down all the overlays

  3. Open Google Chrome and go to:
     http://localhost:3000
     The HLL Command Hub will load in your browser

  4. In Box 1 paste your API URL from Step 2
     The status bar at the top will turn green

  5. Set up your OBS browser sources (see OBS SETUP below)

  6. You are ready to stream!


================================================================
  DAILY USE (every stream)
================================================================

  1. Double-click start.bat
     If an update is available it will install automatically
     Just close and reopen start.bat if prompted

  2. Open http://localhost:3000 in Chrome

  3. Check that your API URL is showing in Box 1 and the
     status bar at the top is green
     If the box is empty or the bar is red:
       - Paste your API URL back in
       - Hit the Save button (💾) to store it for next time
       - You can save multiple servers by name, select them
         from the dropdown, edit the URL and re-save, or
         hit X to delete a saved server you no longer need

  4. Go live!

  To stop the server: close the terminal window
  or click it and press Ctrl+C


================================================================
  CONTROLLING FROM YOUR PHONE
================================================================

  1. Connect your phone to the same WiFi as your PC

  2. Look at the terminal window and find the line:
         Hub (phone): http://192.168.x.x:3000
     The numbers are your PC's IP address on your network

  3. Type that full address into your phone browser
     Do not use localhost — that only works on the PC itself

  4. The phone shows a stripped down control panel with:
       - Allied Faction selector (US / British / Soviets)
       - Team Side Alignment toggle
       - Spotlight Player search box

  5. Any change on your phone shows on the PC hub within
     2 seconds, and any change on the PC shows on your
     phone within 2 seconds

  PHONE SHOWS "SERVER OFFLINE"?
  Use the IP address from the terminal, not localhost.
  Both devices must be on the same WiFi.
  Make sure start.bat is still running.


================================================================
  THE HUB CONTROLS
================================================================

BOX 1 — MATCH API URL
  Paste your HLL CRCON server URL here (from Step 2).
  Saved automatically. Use the dropdown to store multiple
  servers by name — select to load, edit the URL then
  hit Save to update, or X to delete.

BOX 2 — TEAM SIDE ALIGNMENT
  Controls which side of the screen each faction is on.

  STANDARD:  Allied faction on the left (blue)
             Germany on the right (red)

  SWAPPED:   Germany on the left (blue)
             Allied faction on the right (red)

  Blue is always left. Red is always right.
  The faction names are what swap between them.
  Change this to match the uniform colors on the map
  you are playing — some maps put Allies on red side.

BOX 3 — FACTION SELECTION
  Pick which Allied nation is playing this match:
  US ARMY, BRITISH, or SOVIETS.
  Germany is always the Axis faction.
  This replaces the word ALLIES with the actual nation
  name everywhere across all overlays.

BOX 4 — SPOTLIGHT PLAYER
  Type part of any player's name to show their stats
  on the Player Spotlight overlay.
  Typing "smi" will match "JohnSmith" or "SMITH_99".
  Capitalisation does not matter.

  Leave blank to auto-show the top infantry killer.
  Artillery and armor players never appear in auto mode
  no matter how many kills they have — only if you
  specifically type their name.

  Updates within 1-2 seconds of typing.

BOX 5 — TICKER MESSAGES
  Add custom messages that appear inside the Top 5 and
  Top 10 Scroll Banner overlays between player entries.

  HOW TO USE ON PC:
  1. Pick a platform icon (Twitch, YouTube, Discord etc.)
  2. Type your message text
  3. Choose how often it appears (every loop, every 5
     loops, every 2 minutes etc.)
  4. Click Add Message to Ticker
  5. Use the toggle on each saved message to turn it
     on or off without deleting it
  6. The live preview strip shows exactly how it will
     look inside the ticker

  Messages are styled differently from player entries
  with a platform-colored accent bar so viewers can
  clearly tell them apart from kill stats.

  CONTROLLING FROM YOUR PHONE:
  Once messages are saved on the PC hub they appear in
  Box 4 on the phone view. From your phone you can:
  - Toggle any message on or off instantly
  - Change the frequency of any message mid-stream
  Messages must be created on the PC first — the phone
  view only controls messages that already exist.

OBS BROWSER SOURCE URLS
  Each overlay in the hub has a Copy URL button next to it.
  Here is exactly how to use it:

  1. Open the hub at http://localhost:3000
  2. Scroll down to the overlay list at the bottom
  3. Find the overlay you want to add to OBS
  4. Click the Copy URL button next to it
     The URL is now copied to your clipboard
  5. Switch to OBS and follow the steps in OBS SETUP below
  6. Paste the URL when OBS asks for it (Ctrl+V)

  The URLs look like:
  http://localhost:3000/DO_NOT_EDIT_team_compare.html

  These URLs never change so you only need to do this once
  per overlay. OBS will remember them automatically.


================================================================
  OBS SETUP — BROWSER SOURCE RESOLUTIONS
================================================================

Add each overlay as a Browser Source in OBS.
All overlays use one of two canvas sizes:

  ┌──────────────────────────────────────┬──────────┬──────────┐
  │ 3840 x 2160 (4K canvas)             │  Width   │  Height  │
  ├──────────────────────────────────────┼──────────┼──────────┤
  │ Team Comparison                      │  3840 px │  2160 px │
  │ AT Leaderboard                       │          │          │
  │ Melee Leaderboard                    │          │          │
  └──────────────────────────────────────┴──────────┴──────────┘

  ┌──────────────────────────────────────┬──────────┬──────────┐
  │ 1920 x 1080 (Full HD canvas)        │  Width   │  Height  │
  ├──────────────────────────────────────┼──────────┼──────────┤
  │ Player Spotlight                     │  1920 px │  1080 px │
  │ Live Map / Command Dashboard         │          │          │
  │ Kill Streak Alerts                   │          │          │
  │ Kill Feed                            │          │          │
  │ Tank Scoreboard                      │          │          │
  └──────────────────────────────────────┴──────────┴──────────┘

  ┌──────────────────────────────────────┬──────────┬──────────┐
  │ 1920 x 60 (Ticker banner)           │  Width   │  Height  │
  ├──────────────────────────────────────┼──────────┼──────────┤
  │ Top 5 Scroll Banner                  │  1920 px │    60 px │
  │ Top 10 Scroll Banner                 │          │          │
  └──────────────────────────────────────┴──────────┴──────────┘

WHY ARE SOME OVERLAYS 4K?
  The 4K overlays stay sharp when you scale them down in
  OBS. Add them at 3840x2160 then drag the corners in your
  scene to whatever size fits your layout.

HOW TO ADD A BROWSER SOURCE IN OBS:
  1. In your Scene, click the + button under Sources
  2. Choose Browser
  3. Give it a name — e.g. HLL Team Compare
  4. Paste the URL you copied from the bottom inside of the HLL COMMAND HUB (Ctrl+V)
  5. Set Width and Height from the tables above
  6. Click OK
  7. Drag and resize in your scene as needed


================================================================
  WHAT EACH OVERLAY DOES
================================================================

TEAM COMPARISON
  Big side-by-side stat card. Shows kills broken down by
  category: Infantry, Sniper, MG, Armor, AT, Artillery,
  Satchel. Progress bars show which team is winning each
  category. Total kills row at the bottom.
  Updates every 4 seconds.

AT LEADERBOARD
  Top 5 Anti-Tank players ranked by vehicle kills and
  rocket kills. Color coded by faction.
  Updates every 4 seconds.

MELEE LEADERBOARD
  Top 5 knife and shovel killers ranked by total melee
  kills. Color coded by faction.
  Updates every 4 seconds.

PLAYER SPOTLIGHT
  Card in the bottom left showing one player's live stats:
  Kills, Deaths, K/D, KPM, Combat, and top weapon.
  Controlled by Box 4 in the hub.
  Auto shows top infantry killer when box is empty.
  Armor and artillery players never show in auto mode.
  Updates every 3 seconds.

TOP 5 SCROLL BANNER
  Scrolling bar along the bottom showing the top 5
  infantry killers and their stats.
  Armor and artillery players are excluded.
  Updates every 4 seconds.

TOP 10 SCROLL BANNER
  Same as Top 5 but shows 10 players.
  Updates every 4 seconds.

LIVE MAP / COMMAND DASHBOARD
  Two panels. Left: Top 10 infantry leaderboard with
  player names color coded by faction. Right: kill
  breakdown by weapon category including Sniper.
  Armor and artillery excluded from the top 10.
  Updates every 4 seconds.

KILL STREAK ALERTS
  Pop-up alert when any player hits a kill streak
  milestone: 5, 10, 15, 20, or 25 kills without dying.
  Card color and title change based on streak size.
  Artillery players are excluded entirely.
  Resets when the player dies. Checks every 1 second.

KILL FEED
  Live feed in the top right corner showing the last 5
  kills. Killer name, abbreviated weapon, and victim.
  Killer names are color coded by faction.
  Entries fade after 10 seconds. Updates every 1 second.

TANK SCOREBOARD
  Two side panels showing Allied and Axis armor crews.
  Detects tank crews automatically by their weapons.
  Shows crew name, tank type, vehicle kills, infantry
  kills and K/D. Sorted by infantry kills.
  Artillery crews are excluded. Updates every 4 seconds.


================================================================
  FILES IN THIS FOLDER
================================================================

  TOUCH THESE:
  ─────────────
  start.bat     Double-click this to start the server
  README.txt    This guide

  DO NOT OPEN, EDIT, OR RENAME ANYTHING BELOW:
  ──────────────────────────────────────────────
  DO_NOT_EDIT_hub.html               The control hub
  DO_NOT_EDIT_server.py              The server engine
  DO_NOT_EDIT_settings.json          Saved settings
  DO_NOT_EDIT_player.txt             Current spotlight name
  DO_NOT_EDIT_team_compare.html      Team Comparison overlay
  DO_NOT_EDIT_at_leaderboard.html    AT Leaderboard overlay
  DO_NOT_EDIT_melee_leaderboard.html Melee Leaderboard overlay
  DO_NOT_EDIT_player_spotlight.html  Player Spotlight overlay
  DO_NOT_EDIT_top5_scroll_banner.html  Top 5 Scroll Banner
  DO_NOT_EDIT_top10_scroll_banner.html Top 10 Scroll Banner
  DO_NOT_EDIT_map_overlay.html       Command Dashboard overlay
  DO_NOT_EDIT_killstreaks.html       Kill Streak Alerts overlay
  DO_NOT_EDIT_killfeed.html          Kill Feed overlay
  DO_NOT_EDIT_tank_scoreboard.html   Tank Scoreboard overlay
  changelog.md                       Update history
  version.txt                        Current version


================================================================
  TROUBLESHOOTING
================================================================

start.bat says "Python not found"
  Follow the INSTALLING PYTHON section above.
  Make sure you ticked "Add Python to PATH" during install.
  After installing close and reopen start.bat.

"Server offline" in hub
  start.bat is not running — double-click it first.
  Make sure the black terminal window is still open.

Overlays show "Signal Lost" or "Awaiting API"
  Check your API URL in Box 1 is correct and complete.
  Make sure your CRCON server is online and accessible.
  Paste the URL into Chrome to test it — you should see
  a page of data, not an error message.

Stats showing as zero
  The overlays use weapon name keywords to sort kills.
  Make sure your CRCON is returning live match data.
  Try double-clicking the OBS browser source and
  selecting "Refresh cache of current page".

Phone shows "Server offline"
  Use the IP address from the terminal window.
  Do not type localhost on your phone.
  Both devices must be on the same WiFi network.
  Make sure start.bat is running on your PC.

Swap or faction change is slow
  Overlays check for config changes every 1 second.
  Changes apply within 1-4 seconds of clicking.

Spotlight not finding a player
  Try fewer letters — 3 characters is usually enough.
  Spelling must be close — check the actual in-game name.
  Some players use special characters that look like normal
  letters but are not — try a different part of the name.

Tank scoreboard shows "No armor active"
  Tank crews are detected by their weapon signatures.
  The crew must have gotten at least one kill using a
  tank weapon for them to appear on the scoreboard.

Kill Feed shows "Enemy" instead of a victim name
  Victim names are inferred from death count changes.
  In very busy moments with many simultaneous kills the
  match may not always be exact — this is a known limit.


================================================================
  SHARING THIS WITH OTHERS
================================================================

The easiest way is to share the install.bat file.
Each person just needs to:

  1. Download install.bat
  2. Double-click it
  3. It installs Python automatically if needed,
     downloads all files to C:\HLL-Overlay, creates
     a desktop shortcut, and opens the hub

  They will need their own API URL (see STEP 2 above)
  Everything else is handled automatically.
  Updates happen every time start.bat is run.

If install.bat is not available, zip the HLL-Overlay
folder and share it. They will need Python installed
manually (see STEP 1 above) and their own API URL.


================================================================
  VERSION
================================================================
  HLL Command Hub v1.0.6
  Local server build — internet required during use
================================================================
