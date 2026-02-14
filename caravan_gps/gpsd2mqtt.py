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

# STATIC UNIQUE ID - Fixes "Unavailable" entities after reboot
UNIQUE_ID = "caravan_gps"

mqtt_broker = data.get("mqtt_broker") or "core-mosquitto"
mqtt_port = data.get("mqtt_port") or 1883
mqtt_username = sys.argv[1]
mqtt_pw = sys.argv[2]

publish_3d_fix_only = data.get("publish_3d_fix_only", False)
min_n_satellites = data.get("min_n_satellites") or 0
debug = data.get("debug", False)
publish_interval = data.get("publish_interval") or 10

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
        logger.info("HA Restart detected. Sending Discovery Config...")
        publish_discovery()

client.on_connect = on_connect
client.on_message = on_message

def publish_discovery():
    # 1. Location Entity (Device Tracker)
    tracker_config = {
        "unique_id": f"{UNIQUE_ID}_location",
        "name": "Caravan Location",
        "json_attributes_topic": f"{topic_prefix}/attr",
        "icon": "mdi:caravan",
        "source_type": "gps",
        "payload_home": "home",
        "payload_not_home": "not_home",
        "device": {
            "identifiers": [UNIQUE_ID],
            "name": "Caravan GPS System",
            "model": "u-blox 7",
            "manufacturer": "Caravan"
        }
    }
    client.publish(f"{ha_discovery_prefix}/device_tracker/{UNIQUE_ID}/config", json.dumps(tracker_config), retain=True)

    # 2. Satellite Count (Sensor)
    sat_config = {
        "unique_id": f"{UNIQUE_ID}_satellites",
        "name": "GPS Satellites Locked",
        "state_topic": f"{topic_prefix}/satellites",
        "unit_of_measurement": "sat",
        "icon": "mdi:satellite-uplink",
        "device": {
            "identifiers": [UNIQUE_ID]
        }
    }
    client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_sats/config", json.dumps(sat_config), retain=True)
    
    logger.info("MQTT Discovery Sent.")

# --- MAIN LOOP ---
logger.info("Connecting to MQTT...")
client.connect(mqtt_broker, mqtt_port)
client.loop_start()

logger.info("Connecting to GPSD...")
# Retry loop for GPSD connection
while True:
    try:
        # Define client inside loop to handle auto-reconnects
        with GPSDClient(host="127.0.0.1") as gps_client:
            logger.info("GPSD Connected. Streaming Data...")
            
            last_publish = datetime.datetime.now()

            for raw_result in gps_client.json_stream():
                try:
                    result = json.loads(raw_result)
                except:
                    continue

                # --- HANDLE SATELLITES (SKY) ---
                if result.get("class") == "SKY":
                    n_satellites = result.get("uSat", 0)
                    
                    # Publish satellite count immediately
                    client.publish(f"{topic_prefix}/satellites", str(n_satellites))

                # --- HANDLE POSITION (TPV) ---
                elif result.get("class") == "TPV":
                    mode = result.get("mode", 1)
                    
                    # Filter: Only publish if we have a fix (mode 2 or 3)
                    if mode < 2:
                        continue

                    # Home Assistant expects specific keys
                    payload = {
                        "latitude": result.get("lat"),
                        "longitude": result.get("lon"),
                        "altitude": result.get("alt", 0),
                        "gps_accuracy": result.get("epx", 0), # Horizontal error
                        "speed": result.get("speed", 0),
                        "climb": result.get("climb", 0)
                    }

                    # Throttle updates
                    if (datetime.datetime.now() - last_publish).total_seconds() >= publish_interval:
                        client.publish(f"{topic_prefix}/attr", json.dumps(payload))
                        last_publish = datetime.datetime.now()
                        if debug:
                            logger.debug(f"Location Sent: {payload}")

    except Exception as e:
        logger.error(f"GPSD Error or Disconnect: {e}")
        time.sleep(5) # Wait before trying to reconnect to GPSD
