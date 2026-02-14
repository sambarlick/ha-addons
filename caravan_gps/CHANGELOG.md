# Changelog

## 2026.2.14

### Fixed
Startup Lock: Fixed a critical bug where the "Parking Lock" (anti-jitter) prevented the coordinates from populating on startup. If the add-on started while the caravan was parked, the latitude/longitude would stay at 0.0 indefinitely. Added an startup_override check to force the first valid GPS fix to be accepted regardless of vehicle speed.

Discovery Config: Double-checked the Jinja templates in create_config to ensure attributes like accuracy_m attach correctly to their parent sensors without breaking the main state value.

## 2026.2.13

### Fixed
Discovery Logic: Fixed a critical bug in the create_config helper where adding attributes (like accuracy) was accidentally breaking the main State Topic configuration, causing sensors like Latitude and Longitude to report as Unknown or empty.

Attribute Scoping: Completely removed the "Master Sensor" concept. Attributes are now strictly scoped to the sensor they belong to:

sensor.caravan_latitude → accuracy_m

sensor.caravan_speed → speed_ms

sensor.caravan_heading → bearing_deg

sensor.caravan_elevation → vertical_accuracy_m

### Changed
Code Cleanliness: Flattened the internal state dictionary (current_state) to make it easier to maintain and less prone to "nested dictionary" errors in Jinja templates.

## 2026.2.12
### Changed
Architecture Overhaul: Removed the "Master Sensor" concept. MQTT payloads are now properly filtered so that attributes are only attached to their relevant entities.
sensor.caravan_speed now holds the speed_ms attribute.
sensor.caravan_heading now holds the bearing (degrees) attribute.
sensor.caravan_latitude and longitude now hold the accuracy_m attribute.
sensor.caravan_elevation now holds the vertical_accuracy_m attribute.
binary_sensor.caravan_gps_fix_status now holds the mode (e.g., "3D Fix") attribute.
Data Hygiene: The internal current_state dictionary was flattened to make templating cleaner and more reliable.

### Fixed
Jitter Control: Parking Lock logic (Speed < 3.6km/h) is retained and active.
Accuracy Reporting: Split accuracy into Horizontal (accuracy_m) for coordinates and Vertical (accuracy_v) for elevation, providing more precise tolerance data for the Altimeter.

## 2026.2.11

### Fixed
Anti-Jitter (Parking Lock): Implemented a "Static Navigation" logic. When the caravan speed drops below 3.6 km/h (parked), the script stops updating Latitude, Longitude, and Elevation. This eliminates 100% of the "map wander" or "jitter" while the caravan is stationary.
Precision Rounding: When moving, coordinates are now rounded to 6 decimal places (~11cm) to filter out signal noise.

### Changed
Attribute Cleanup: Confirmed that sensor.caravan_latitude acts as the "Master Sensor" holding all technical data (Speed, Heading, Accuracy) in its attributes for advanced diagnostics.

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
