# HLL Command Hub — Changelog

## v1.0.8
- Replaced emoji platform icons with proper SVG brand icons (Twitch, YouTube, TikTok, X, Discord, Instagram)
- Fixed ticker messages not appearing in Top 5 and Top 10 scroll banners
- Hub now pushes ticker messages to server every 5 seconds to keep overlays in sync
- SVG icons now render correctly in hub, preview strip, phone view, and ticker overlays

## v1.0.7
- Added Ticker Messages system to hub (Box 5)
- Add multiple custom messages to the Top 5 and Top 10 scroll banners
- Choose platform icon per message: General, Twitch, YouTube, TikTok, X, Discord, Instagram
- Set frequency per message: every loop, every 3/5/10 loops, every 2/5 minutes
- Toggle individual messages on/off without deleting them
- Live preview strip in hub shows exactly how messages look in the ticker
- Messages persist between sessions and sync to overlays instantly
- Phone view (Box 4) shows saved messages from desktop — toggle on/off and change frequency per message from your phone mid-stream
- Messages must be created on the PC hub first before they appear on the phone view
- Updated README with ticker messages section

## v1.0.6
- Fixed auto-updater downloading files to wrong folder on some systems
- Server now always runs from its own folder regardless of where start.bat is launched from

## v1.0.5
- Added Melee Leaderboard overlay — Top 5 knife and shovel killers, faction color coded, 3840x2160
- Added Soviets faction pill highlight fix in hub
- Added hint label under saved servers dropdown explaining how to edit/delete
- Fixed 150mm Howitzer not being counted as artillery in Team Comparison and Map Overlay
- Fixed 105mm Howitzer (Sherman SPA) being double-counted as armor and artillery
- Fixed SPG crews appearing in infantry lists across all overlays
- Artillery kills now locked to artillery category only — cannot bleed into armor or infantry
- Artillery crews excluded from Kill Streak alerts

## v1.0.4
- Fixed auto-updater version loop — server.py no longer auto-updates itself
- Users can now drag all files into GitHub without causing update conflicts
- HTML overlays still auto-update as normal

## v1.0.3
- Added Sniper category to Team Comparison and Map Overlay
- Added Total Kills row to Team Comparison
- Added Tank Scoreboard overlay — Allied vs Axis armor crews with vehicle kills, infantry kills and K/D
- Added Top 10 Scroll Banner overlay
- Renamed Bottom Ticker to Top 5 Scroll Banner in hub
- Fixed 150mm Howitzer not being counted as artillery
- Fixed 105mm Howitzer being double-counted as armor and artillery
- Fixed SPG crews appearing in Top 5, Top 10, Map Overlay infantry lists
- Artillery kills now correctly counted toward artillery category only
- Artillery crews excluded from Kill Streak alerts
- Tank scoreboard broad keyword detection for vehicle names
- Tank scoreboard sorts by infantry kills
- Kill Feed entries fade after 10 seconds
- Kill Feed polls every 1 second
- Kill Feed centered layout, victim names inferred from death delta
- Weapon abbreviations added to Kill Feed
- Kill Streak baseline fixed — no spam on OBS load
- Kill Streak polls every 1 second

## v1.0.2
- Added Kill Feed overlay
- Added saved servers dropdown to hub
- Added faction selector (US Army / British / Soviets)
- Added auto-updater with changelog display
- Fixed server root URL redirecting to hub
- Fixed legacy filename redirects for old OBS sources
- DO_NOT_EDIT prefix added to all files
- Phone view syncs with PC hub bidirectionally

## v1.0.1
- Fixed team comparison showing wrong stats after faction selector added
- Fixed armor/artillery exclusion across all overlays
- All overlays poll config every 1 second for instant hub changes
- Server switched to ThreadingHTTPServer for stability

## v1.0.0
- Initial release
- Local server system — no internet required during streams
- Hub control panel with phone support
- Team Comparison, AT Leaderboard, Player Spotlight overlays
- Command Dashboard, Kill Streak Alerts overlays
- Auto-updater via GitHub
