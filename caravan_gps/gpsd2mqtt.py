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
        # Run cleanup first, then publish new config
        cleanup_old_entities()
        publish_discovery()
    else:
        logger.error(f"Failed to connect to MQTT: {rc}")

def on_message(client, userdata, msg):
    if msg.topic == "homeassistant/status" and msg.payload.decode() == "online":
        publish_discovery()

client.on_connect = on_connect
client.on_message = on_message

def cleanup_old_entities():
    """Sends empty payloads to clear out old/ghost entities from previous versions."""
    logger.info("Running cleanup of old entities...")
    
    # 1. Kill the old Device Tracker (The Home/Away sensor)
    client.publish(f"{ha_discovery_prefix}/device_tracker/{UNIQUE_ID}_location/config", "", retain=True)
    client.publish(f"{ha_discovery_prefix}/device_tracker/{UNIQUE_ID}/config", "", retain=True)
    
    # 2. Kill old/duplicate Satellite sensors from previous versions
    client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_satellites/config", "", retain=True)
    client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_sats/config", "", retain=True)
    
    logger.info("Cleanup commands sent.")

def publish_discovery():
    device_info = {
        "identifiers": [UNIQUE_ID],
        "name": "Caravan GPS System",
        "model": "u-blox 7",
        "manufacturer": "Caravan"
    }

    # Helper to create sensor config
    def create_config(name, uid_suffix, template, unit=None, icon=None, device_class=None, attributes=False):
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
        
        # Add attributes topic if requested (for Accuracy, etc)
        if attributes:
             config["json_attributes_topic"] = f"{topic_prefix}/attr"
        
        # Publish
        client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_{uid_suffix}/config", json.dumps(config), retain=True)

    # --- 1. SATELLITES (Locked & Total) ---
    # We use a separate topic 'satellites' for these to ensure they update on SKY messages
    
    # LOCKED (Used)
    sat_locked_config = {
        "unique_id": f"{UNIQUE_ID}_satellites_locked",
        "name": "GPS Satellites Locked",
        "state_topic": f"{topic_prefix}/satellites",
        "value_template": "{{ value_json.used }}",
        "unit_of_measurement": "sat",
        "icon": "mdi:satellite-uplink",
        "device": device_info
    }
    client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_sats_locked/config", json.dumps(sat_locked_config), retain=True)

    # TOTAL (Visible)
    sat_total_config = {
        "unique_id": f"{UNIQUE_ID}_satellites_total",
        "name": "GPS Satellites Total",
        "state_topic": f"{topic_prefix}/satellites",
        "value_template": "{{ value_json.visible }}",
        "unit_of_measurement": "sat",
        "icon": "mdi:satellite-variant",
        "device": device_info
    }
    client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_sats_total/config", json.dumps(sat_total_config), retain=True)
    
    # HDOP
    hdop_config = {
        "unique_id": f"{UNIQUE_ID}_hdop",
        "name": "GPS HDOP",
        "state_topic": f"{topic_prefix}/satellites",
        "value_template": "{{ value_json.hdop }}",
        "icon": "mdi:target",
        "device": device_info
    }
    client.publish(f"{ha_discovery_prefix}/sensor/{UNIQUE_ID}_hdop/config", json.dumps(hdop_config), retain=True)


    # --- 2. MAIN SENSORS ---
    # These read from the 'attr' topic
    create_config("Caravan Latitude", "lat", "{{ value_json.latitude }}", icon="mdi:latitude", attributes=True)
    create_config("Caravan Longitude", "lon", "{{ value_json.longitude }}", icon="mdi:longitude", attributes=True)
    
    create_config("Caravan Speed", "speed", "{{ value_json.speed | float(0) | round(1) }}", unit="m/s", device_class="speed")
    create_config("Caravan Elevation", "alt", "{{ value_json.altitude | float(0) | round(1) }}", unit="m", device_class="distance", icon="mdi:elevation-rise")
    create_config("Caravan Climb", "climb", "{{ value_json.climb | float(0) | round(1) }}", unit="m/s", icon="mdi:arrow-up-bold")
    create_config("Caravan Mode", "mode", "{{ value_json.mode_str }}", icon="mdi:crosshairs-gps")
    create_config("Caravan Time", "time", "{{ value_json.time }}", device_class="timestamp")

    logger.info("MQTT Discovery Sent: Cleanup + New Sensors.")

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
                    # Fix for "Total Satellites" showing empty
                    # We ensure 'visible' is always sent as an integer
                    sat_payload = {
                        "used": int(result.get("uSat", 0)),
                        "visible": int(result.get("nSat", 0)),
                        "hdop": float(result.get("hdop", 99.9))
                    }
                    client.publish(f"{topic_prefix}/satellites", json.dumps(sat_payload))

                elif result.get("class") == "TPV":
                    mode = result.get("mode", 1)
                    if mode < 2: continue

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
                        "mode_str": mode_str,
                        # Adding extra attributes for the UI
                        "accuracy_m": result.get("epx", 0),
                        "satellites_used": result.get("uSat", 0) # Redundant but useful for attributes
                    }

                    if (datetime.datetime.now() - last_publish).total_seconds() >= publish_interval:
                        client.publish(f"{topic_prefix}/attr", json.dumps(payload))
                        last_publish = datetime.datetime.now()

    except Exception as e:
        logger.error(f"GPSD Error: {e}")
        time.sleep(5)
