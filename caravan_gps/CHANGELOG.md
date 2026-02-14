# Changelog

## 2026.2.3

### Added
- **Dedicated Sensors:** The Add-on now automatically discovers separate sensors for **Speed** (m/s) and **Altitude** (m) in Home Assistant. You no longer need to dig into attributes to find this data.
- **Enhanced Discovery:** Updated `gpsd2mqtt.py` to push a full suite of entities (Tracker, Satellites, Speed, Altitude) grouped under a single "Caravan GPS System" device.

### Changed
- **Entity Logic:** Moved away from hiding data inside the Device Tracker attributes. Now uses the "Best of Both Worlds" approach: a Device Tracker for the map/presence, and individual Sensors for data logging and graphing.

## 2026.2.2

### Fixed
- **Startup Hanging:** Fixed a critical bug where `gpsd` was blocking the startup script, preventing the MQTT bridge (Python script) from ever launching.
- **Process Management:** Updated `run.sh` to explicitly background (`&`) the `gpsd` process and added the `-N` flag to prevent double-daemonizing.

## 2026.2.1

### Fixed
- **Persistent Entities:** Fixed issue where entities (Location, Satellite Count) became "Unavailable" or created duplicates after every reboot. Now uses a static Unique ID (`caravan_gps`).
- **Read-Only Error:** Fixed `gpsd` crashing or throwing "Read-only file system" errors on Home Assistant OS by adding the `-b` (broken-safe) flag.
- **Connection Stability:** Forced `gpsd` to listen on all interfaces (`-G`) and start immediately (`-n`) to prevent connection timeouts.

### Changed
- **Default Device:** Updated default device path to specific u-blox ID for better hardware detection.
- **Satellite Logic:** Improved handling of satellite data to report "0" instead of going unavailable when signal is lost.
- **Repository URL:** Corrected internal links to point to the `sambarlick` repository.
