# Changelog

## 2026.2.10

### Added
Feature: Added Compass Direction translation. Heading is now displayed as "N", "NW", "SE", etc., instead of raw degrees.
Sensor: sensor.caravan_heading (Compass Direction).
Attributes: The sensor.caravan_latitude entity now includes a full set of technical attributes in the "More Info" dialog, including:
accuracy_m (GPS Error in meters)
heading_deg (Raw 360° heading)
speed_kmh (Raw speed)
gradient

### Changed
Logic: Heading updates are now "Locked" when the vehicle is stationary (Speed < 1.0 m/s). This prevents the compass sensor from spinning wildly due to GPS drift when parked.

### Fixed
Cleanliness: Removed the need for separate sensors for Accuracy and Raw Heading by moving them to attributes, keeping the dashboard clean.

## 2026.2.9

### Fixed
Mode Translation: Fixed a bug where sensor.caravan_gps_mode was reporting as empty/blank. The script now correctly translates the raw GPSD mode integers (2, 3) into human-readable text (2D Fix, 3D Fix).
Startup State: Added a default value ("No Fix") to the internal state to prevent the Mode sensor from being Unknown on startup before the first GPS packet arrives.

### Changed
Entity Naming: Renamed the "Caravan Mode" sensor to "Caravan GPS Mode" to be more descriptive and avoid confusion with other system modes (e.g., alarm or sleep modes).

## 2026.2.8

### Added
Sensor: binary_sensor.caravan_gps_fix_status (Connected/Lost). This replaces the vague "seconds ago" time check with a clear connectivity status.
Sensor: sensor.caravan_gradient (Climbing ↗️ / Descending ↘️ / Level ➡️). Replaces the raw "Climb" (m/s) sensor with human-readable text.

### Changed
Unit Conversion: Speed is now reported in km/h (previously m/s) to match standard vehicle speedometers.
Time Format: sensor.caravan_gps_time now displays as a static clock (e.g., 14:32:01) rather than a relative "seconds ago" timestamp.
State Persistence: Implemented a caching system to prevent data (Altitude, Speed) from flickering to 0 or Unknown between GPS packets.
Jitter Filter: Added a threshold (1.0 m/s) to force Speed to 0 km/h when the caravan is parked, eliminating GPS drift.

### Fixed
Satellite Glitch: Added logic to ignore "0 Satellite" reports if the GPS still maintains a valid 2D/3D fix.

## 2026.2.7

### Fixed
- **Cleanup:** Added aggressive "Nuke" logic to force the removal of stuck Device Trackers and duplicate Ghost entities from versions 2026.2.3 and older.


## 2026.2.5

### Added
- **Sensor:** `sensor.caravan_satellites_total` (Visible satellites).
- **Sensor:** `sensor.caravan_hdop` (GPS Precision/Quality).
- **Attribute:** Added `accuracy_m` to Latitude/Longitude sensors.

### Removed
- **Device Tracker:** Removed the "Location" (Home/Away) entity to reduce clutter.


## 2026.2.4

### Changed
- **Full Sensor Split:** Removed the `device_tracker` entirely.
- **New Entities:** Latitude and Longitude are now separate sensors (`sensor.caravan_latitude`, `sensor.caravan_longitude`).
- **Added:** Added `Climb`, `Mode`, and `Time` sensors to match the standard GPSD integration feature set.
- **Organization:** All data is now organized as individual sensors under the "Caravan GPS System" device.

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
