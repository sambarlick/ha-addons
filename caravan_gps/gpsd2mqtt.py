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

# --- HELPER FUNCTIONS ---
def degrees_to_cardinal(d):
    """
    Converts degrees (0-360) to 16-point Compass directions.
    """
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((d + 11.25)/22.5)
    return dirs[ix % 16]

# --- MQTT SETUP ---
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_pw)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Broker.")
        client.subscribe("homeassistant/status")
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
    """Aggressively clears ALL previous discovery topics."""
    logger.info("Cleaning up legacy entities...")
    ghosts = [
        f"{ha_discovery_prefix}/device_tracker/{UNIQUE_ID}/config",
        f"{ha_discovery_prefix}/device_tracker/{UNIQUE_ID}_location/config",
        f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_sats/config",
        f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_satellites/config",
        f"{ha_discovery_prefix}/sensor/gps_satellites_locked/config",
        f"{ha_discovery_prefix}/sensor/caravan_gps_system_gps_satellites_locked/config",
        f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_climb/config"
    ]
    for topic in ghosts:
        client.publish(topic, "", retain=True)
    logger.info("Cleanup complete.")

def publish_discovery():
    device_info = {
        "identifiers": [UNIQUE_ID],
        "name": "Caravan GPS System",
        "model": "u-blox 7",
        "manufacturer": "Caravan"
    }

    def create_config(name, uid_suffix, template, unit=None, icon=None, device_class=None, value_topic=None, attributes=False):
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
        
        # KEY FEATURE: If attributes=True, we point to the main payload
        if attributes:
            config["json_attributes_topic"] = topic
            config["json_attributes_template"] = "{{ value_json | tojson }}"

        client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_{uid_suffix}/config", json.dumps(config), retain=True)

    # --- 1. Fix Status ---
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

    # --- 2. Heading (Cardinal Direction) ---
    # We display the text (e.g., "NW") but the raw degrees will be in attributes
    create_config("Caravan Heading", "heading", "{{ value_json.heading_cardinal }}", icon="mdi:compass")

    # --- 3. Speed ---
    create_config("Caravan Speed", "speed", "{{ value_json.speed_kmh | float(0) | round(1) }}", unit="km/h", device_class="speed", icon="mdi:speedometer")

    # --- 4. Gradient ---
    create_config("Caravan Gradient", "gradient", "{{ value_json.gradient }}", icon="mdi:slope-uphill")

    # --- 5. Time ---
    create_config("GPS Atomic Time", "time", "{{ value_json.time_str }}", icon="mdi:clock-digital")

    # --- 6. Latitude (WITH ATTRIBUTES) ---
    # This is the "Master" sensor that holds all the technical data in its attributes
    create_config("Caravan Latitude", "lat", "{{ value_json.latitude }}", icon="mdi:latitude", attributes=True)
    
    # --- 7. Longitude ---
    create_config("Caravan Longitude", "lon", "{{ value_json.longitude }}", icon="mdi:longitude")
    
    # --- 8. Elevation ---
    create_config("Caravan Elevation", "alt", "{{ value_json.altitude | float(0) | round(1) }}", unit="m", icon="mdi:elevation-rise")
    
    # --- 9. Mode ---
    create_config("Caravan GPS Mode", "mode", "{{ value_json.mode_str }}", icon="mdi:crosshairs-gps")

    # --- 10. Satellite Sensors ---
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

# State persistence
current_state = {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "speed_kmh": 0.0,
    "gradient": "Level ➡️",
    "heading_deg": 0.0,
    "heading_cardinal": "N",
    "accuracy_m": 0.0,
    "time_str": "--:--:--",
    "fix_status": "Lost",
    "mode": 1,
    "mode_str": "No Fix"
}

while True:
    try:
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
                    current_state["mode"] = mode 
                    
                    if mode == 1: current_state["mode_str"] = "No Fix"
                    elif mode == 2: current_state["mode_str"] = "2D Fix"
                    elif mode == 3: current_state["mode_str"] = "3D Fix"

                    # Binary Sensor Logic
                    if mode < 2:
                        current_state["fix_status"] = "Lost"
                    else:
                        current_state["fix_status"] = "Connected"
                        
                        if "lat" in result: current_state["latitude"] = result["lat"]
                        if "lon" in result: current_state["longitude"] = result["lon"]
                        if "alt" in result: current_state["altitude"] = result["alt"]
                        
                        # TIME
                        if "time" in result:
                            try:
                                ts = result["time"]
                                if "T" in ts:
                                    time_part = ts.split("T")[1].split(".")[0] 
                                    current_state["time_str"] = time_part
                            except:
                                pass

                        # SPEED & HEADING
                        raw_speed_ms = float(result.get("speed", 0))
                        
                        # Only update heading if we are actually moving (> 1.0 m/s)
                        # Otherwise the compass spins wildly while parked.
                        if raw_speed_ms > 1.0:
                            current_state["speed_kmh"] = raw_speed_ms * 3.6
                            
                            # HEADING LOGIC
                            if "track" in result:
                                heading = float(result["track"])
                                current_state["heading_deg"] = heading
                                current_state["heading_cardinal"] = degrees_to_cardinal(heading)
                        else:
                            current_state["speed_kmh"] = 0.0
                            # We keep the last known heading when stopped

                        # ACCURACY (EPX/EPY)
                        if "epx" in result and "epy" in result:
                            # Use max error of lat or lon
                            max_err = max(float(result.get("epx", 0)), float(result.get("epy", 0)))
                            current_state["accuracy_m"] = round(max_err, 1)

                        # GRADIENT
                        if "climb" in result:
                            climb = float(result["climb"])
                            if climb > 0.5: current_state["gradient"] = "Climbing ↗️"
                            elif climb < -0.5: current_state["gradient"] = "Descending ↘️"
                            else: current_state["gradient"] = "Level ➡️"

                    # Publish interval
                    if (datetime.datetime.now() - last_publish).total_seconds() >= publish_interval:
                        client.publish(f"{topic_prefix}/attr", json.dumps(current_state))
                        last_publish = datetime.datetime.now()

    except Exception as e:
        logger.error(f"GPSD Connection Error: {e}")
        time.sleep(5)
