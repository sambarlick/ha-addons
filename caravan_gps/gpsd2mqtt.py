import json
import datetime
import logging
import time
import sys
import paho.mqtt.client as mqtt
from gpsdclient import GPSDClient

# --- CONFIGURATION ---
with open("/data/options.json", "r") as jsonfile:
    data = json.load(jsonfile)

UNIQUE_ID = "caravan_gps"

mqtt_broker = data.get("mqtt_broker") or "core-mosquitto"
mqtt_port = data.get("mqtt_port") or 1883
mqtt_username = sys.argv[1]
mqtt_pw = sys.argv[2]

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
        publish_discovery()
    else:
        logger.error(f"Failed to connect to MQTT: {rc}")

def on_message(client, userdata, msg):
    if msg.topic == "homeassistant/status" and msg.payload.decode() == "online":
        publish_discovery()

client.on_connect = on_connect
client.on_message = on_message

def publish_discovery():
    device_info = {
        "identifiers": [UNIQUE_ID],
        "name": "Caravan GPS System",
        "model": "u-blox 7",
        "manufacturer": "Caravan"
    }

    # Helper to create sensor config
    def create_config(name, uid_suffix, template, unit=None, icon=None, device_class=None):
        config = {
            "unique_id": f"{UNIQUE_ID}_{uid_suffix}",
            "name": name,
            "state_topic": f"{topic_prefix}/attr",
            "value_template": template,
            "device": device_info
        }
        if unit: config["unit_of_measurement"] = unit
        if icon: config["icon"] = icon
        if device_class: config["device_class"] = device_class
        
        # Publish
        client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_{uid_suffix}/config", json.dumps(config), retain=True)

    # --- 1. LATITUDE & LONGITUDE (SEPARATED) ---
    create_config("Caravan Latitude", "lat", "{{ value_json.latitude }}", icon="mdi:latitude")
    create_config("Caravan Longitude", "lon", "{{ value_json.longitude }}", icon="mdi:longitude")

    # --- 2. SATELLITES (SEPARATE TOPIC) ---
    # Satellites come from a different message type, so we configure it manually
    sat_config = {
        "unique_id": f"{UNIQUE_ID}_satellites",
        "name": "GPS Satellites Locked",
        "state_topic": f"{topic_prefix}/satellites",
        "unit_of_measurement": "sat",
        "icon": "mdi:satellite-uplink",
        "device": device_info
    }
    client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_sats/config", json.dumps(sat_config), retain=True)

    # --- 3. OTHER SENSORS ---
    create_config("Caravan Speed", "speed", "{{ value_json.speed | float(0) | round(1) }}", unit="m/s", device_class="speed")
    create_config("Caravan Elevation", "alt", "{{ value_json.altitude | float(0) | round(1) }}", unit="m", device_class="distance", icon="mdi:elevation-rise")
    create_config("Caravan Climb", "climb", "{{ value_json.climb | float(0) | round(1) }}", unit="m/s", icon="mdi:arrow-up-bold")
    create_config("Caravan Mode", "mode", "{{ value_json.mode_str }}", icon="mdi:crosshairs-gps")
    create_config("Caravan Time", "time", "{{ value_json.time }}", device_class="timestamp")

    logger.info("MQTT Discovery Sent: All Sensors Separated.")

# --- MAIN LOOP ---
client.connect(mqtt_broker, mqtt_port)
client.loop_start()

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

                if result.get("class") == "SKY":
                    n_satellites = result.get("uSat", 0)
                    client.publish(f"{topic_prefix}/satellites", str(n_satellites))

                elif result.get("class") == "TPV":
                    mode = result.get("mode", 1)
                    if mode < 2: continue

                    # Map mode number to text
                    mode_str = "No Fix"
                    if mode == 2: mode_str = "2D Fix"
                    if mode == 3: mode_str = "3D Fix"

                    payload = {
                        "latitude": result.get("lat"),
                        "longitude": result.get("lon"),
                        "altitude": result.get("alt", 0),
                        "speed": result.get("speed", 0),
                        "climb": result.get("climb", 0),
                        "time": result.get("time"),
                        "mode_str": mode_str
                    }

                    if (datetime.datetime.now() - last_publish).total_seconds() >= publish_interval:
                        client.publish(f"{topic_prefix}/attr", json.dumps(payload))
                        last_publish = datetime.datetime.now()

    except Exception as e:
        logger.error(f"GPSD Error: {e}")
        time.sleep(5)
