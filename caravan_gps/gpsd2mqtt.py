import json
import datetime
import logging
import time
import sys
import paho.mqtt.client as mqtt
from gpsdclient import GPSDClient

# --- CONFIGURATION ---
try:
    with open("/data/options.json", "r") as jsonfile:
        data = json.load(jsonfile)
except FileNotFoundError:
    data = {}

UNIQUE_ID = "caravan_gps"

mqtt_broker = data.get("mqtt_broker") or "core-mosquitto"
mqtt_port = data.get("mqtt_port") or 1883
mqtt_username = sys.argv[1] if len(sys.argv) > 1 else "mqtt"
mqtt_pw = sys.argv[2] if len(sys.argv) > 2 else "password"

publish_interval = data.get("publish_interval") or 10
debug = data.get("debug", False)

# MQTT Topics
topic_prefix = f"gpsd2mqtt/{UNIQUE_ID}"
ha_discovery_prefix = "homeassistant"

# --- LOGGING ---
logging.basicConfig(
    level=logging.DEBUG if debug else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GPS_MQTT")

# --- MQTT SETUP ---
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_pw)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Broker.")
        client.subscribe("homeassistant/status")
        # Run the Nuke first!
        nuke_legacy_entities()
        publish_discovery()
    else:
        logger.error(f"Failed to connect to MQTT: {rc}")

def on_message(client, userdata, msg):
    if msg.topic == "homeassistant/status" and msg.payload.decode() == "online":
        publish_discovery()

client.on_connect = on_connect
client.on_message = on_message

def nuke_legacy_entities():
    """Aggressively clears ALL previous discovery topics to prevent duplicates."""
    logger.info("Executing cleanup of legacy ghosts...")
    
    ghosts = [
        # Old Location Tracker
        f"{ha_discovery_prefix}/device_tracker/{UNIQUE_ID}/config",
        f"{ha_discovery_prefix}/device_tracker/{UNIQUE_ID}_location/config",
        # Old Single Satellite sensors
        f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_sats/config",
        f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_satellites/config",
        # Old Raw sensors
        f"{ha_discovery_prefix}/sensor/gps_satellites_locked/config",
        f"{ha_discovery_prefix}/sensor/caravan_gps_system_gps_satellites_locked/config",
        # Previous Iteration sensors
        f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_climb/config" # We replaced Climb with Gradient
    ]
    
    for topic in ghosts:
        client.publish(topic, "", retain=True)
    
    logger.info("Legacy ghosts nuked.")

def publish_discovery():
    device_info = {
        "identifiers": [UNIQUE_ID],
        "name": "Caravan GPS System",
        "model": "u-blox 7",
        "manufacturer": "Caravan"
    }

    # Helper for creating sensor configs
    def create_config(name, uid_suffix, template, unit=None, icon=None, device_class=None, value_topic=None):
        topic = value_topic if value_topic else f"{topic_prefix}/attr"
        config = {
            "unique_id": f"{UNIQUE_ID}_{uid_suffix}",
            "name": name,
            "state_topic": topic,
            "value_template": template,
            "device": device_info
        }
        if unit: config["unit_of_measurement"] = unit
        if icon: config["icon"] = icon
        if device_class: config["device_class"] = device_class
        
        client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_{uid_suffix}/config", json.dumps(config), retain=True)

    # --- 1. NEW: Binary Sensor for Fix Status ---
    fix_config = {
        "unique_id": f"{UNIQUE_ID}_fix_status",
        "name": "GPS Fix Status",
        "state_topic": f"{topic_prefix}/attr",
        "value_template": "{{ value_json.fix_status }}",
        "device_class": "connectivity",
        "payload_on": "Connected",
        "payload_off": "Lost",
        "device": device_info
    }
    client.publish(f"{ha_discovery_prefix}/binary_sensor/{UNIQUE_ID}_fix_status/config", json.dumps(fix_config), retain=True)

    # --- 2. UPDATED: Speed in km/h ---
    create_config("Caravan Speed", "speed", "{{ value_json.speed_kmh | float(0) | round(1) }}", unit="km/h", device_class="speed", icon="mdi:speedometer")

    # --- 3. UPDATED: Gradient Text Sensor ---
    create_config("Caravan Gradient", "gradient", "{{ value_json.gradient }}", icon="mdi:slope-uphill")

    # --- 4. UPDATED: Time (String format) ---
    create_config("GPS Atomic Time", "time", "{{ value_json.time_str }}", icon="mdi:clock-digital")

    # --- 5. STANDARD SENSORS ---
    create_config("Caravan Latitude", "lat", "{{ value_json.latitude }}", icon="mdi:latitude")
    create_config("Caravan Longitude", "lon", "{{ value_json.longitude }}", icon="mdi:longitude")
    create_config("Caravan Elevation", "alt", "{{ value_json.altitude | float(0) | round(1) }}", unit="m", icon="mdi:elevation-rise")
    
    # --- 6. SATELLITE SENSORS ---
    sat_locked = {
        "unique_id": f"{UNIQUE_ID}_satellites_locked",
        "name": "GPS Satellites Locked",
        "state_topic": f"{topic_prefix}/satellites",
        "value_template": "{{ value_json.used }}",
        "unit_of_measurement": "sat",
        "icon": "mdi:satellite-uplink",
        "device": device_info
    }
    client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_sats_locked/config", json.dumps(sat_locked), retain=True)
    
    sat_total = {
        "unique_id": f"{UNIQUE_ID}_satellites_total",
        "name": "GPS Satellites Total",
        "state_topic": f"{topic_prefix}/satellites",
        "value_template": "{{ value_json.visible }}",
        "unit_of_measurement": "sat",
        "icon": "mdi:satellite-variant",
        "device": device_info
    }
    client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_sats_total/config", json.dumps(sat_total), retain=True)
    
    hdop_config = {
        "unique_id": f"{UNIQUE_ID}_hdop",
        "name": "GPS HDOP",
        "state_topic": f"{topic_prefix}/satellites",
        "value_template": "{{ value_json.hdop }}",
        "icon": "mdi:target",
        "device": device_info
    }
    client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_hdop/config", json.dumps(hdop_config), retain=True)

    logger.info("MQTT Discovery Sent.")

# --- MAIN LOOP ---
client.connect(mqtt_broker, mqtt_port)
client.loop_start()

# State persistence: These are the defaults until real data arrives
current_state = {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "speed_kmh": 0.0,
    "gradient": "Level ➡️",
    "time_str": "--:--:--",
    "fix_status": "Lost",
    "mode": 1 # 1=No Fix, 2=2D, 3=3D
}

while True:
    try:
        # Connect to GPSD
        with GPSDClient(host="127.0.0.1") as gps_client:
            logger.info("GPSD Connected.")
            last_publish = datetime.datetime.now()

            for raw_result in gps_client.json_stream():
                try:
                    result = json.loads(raw_result)
                except:
                    continue

                # --- SATELLITES (SKY) ---
                if result.get("class") == "SKY":
                    n_sat = int(result.get("nSat", 0))
                    
                    # LOGIC: If we have a fix (mode > 1), ignore 0 sats as a glitch.
                    # If we have NO fix (mode <= 1), 0 sats is real.
                    if n_sat == 0 and current_state["mode"] > 1:
                        continue
                        
                    sat_payload = {
                        "used": int(result.get("uSat", 0)),
                        "visible": n_sat,
                        "hdop": float(result.get("hdop", 99.9))
                    }
                    client.publish(f"{topic_prefix}/satellites", json.dumps(sat_payload))

                # --- POSITION (TPV) ---
                elif result.get("class") == "TPV":
                    mode = result.get("mode", 1)
                    current_state["mode"] = mode # Update state for the Sky check logic

                    # Binary Sensor Logic
                    if mode < 2:
                        current_state["fix_status"] = "Lost"
                        # If lost, we keep old position data but mark status as lost
                    else:
                        current_state["fix_status"] = "Connected"
                        
                        # Only update data if we have a fix AND the key exists in the packet
                        if "lat" in result: current_state["latitude"] = result["lat"]
                        if "lon" in result: current_state["longitude"] = result["lon"]
                        if "alt" in result: current_state["altitude"] = result["alt"]
                        
                        # TIME LOGIC: Convert ISO to HH:MM:SS
                        if "time" in result:
                            # TPV time is usually "2023-10-27T10:00:00.000Z"
                            try:
                                ts = result["time"]
                                # Simple string slice to get HH:MM:SS
                                if "T" in ts:
                                    time_part = ts.split("T")[1].split(".")[0] 
                                    current_state["time_str"] = time_part
                            except:
                                pass

                        # SPEED LOGIC: Convert m/s to km/h and apply jitter filter
                        raw_speed_ms = float(result.get("speed", 0))
                        # Threshold 1.0 m/s = 3.6 km/h. If slower, report 0.
                        if raw_speed_ms < 1.0:
                            current_state["speed_kmh"] = 0.0
                        else:
                            current_state["speed_kmh"] = raw_speed_ms * 3.6

                        # CLIMB/GRADIENT LOGIC
                        if "climb" in result:
                            climb = float(result["climb"])
                            if climb > 0.5:
                                current_state["gradient"] = "Climbing ↗️"
                            elif climb < -0.5:
                                current_state["gradient"] = "Descending ↘️"
                            else:
                                current_state["gradient"] = "Level ➡️"

                    # Throttle Publishing to avoid MQTT spam
                    if (datetime.datetime.now() - last_publish).total_seconds() >= publish_interval:
                        client.publish(f"{topic_prefix}/attr", json.dumps(current_state))
                        last_publish = datetime.datetime.now()

    except Exception as e:
        logger.error(f"GPSD Connection Error: {e}")
        time.sleep(5) # Wait 5 seconds before retrying connection
