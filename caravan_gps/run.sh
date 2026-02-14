#!/usr/bin/with-contenv bashio

# --- CONFIGURATION ---
INPUT_TYPE=$(bashio::config 'input_type')
DEVICE=$(bashio::config 'device')
BAUDRATE=$(bashio::config 'baudrate' 9600)
GPSD_USER_OPTIONS=$(bashio::config 'gpsd_options')

# FORCE these flags for stability:
# -n: Don't wait for client (start now)
# -G: Listen on all interfaces (crucial for HA to see it)
# -b: Read-only/Broken-safe (Prevents the "chmod failed" error on HAOS)
GPSD_OPTIONS="-n -G -b ${GPSD_USER_OPTIONS}"

GPSD_SOCKET="/var/run/gpsd.sock"

# --- MQTT AUTHENTICATION ---
# Automatically grab credentials from the Home Assistant Mosquitto Service
if bashio::config.is_empty 'mqtt_username' && bashio::var.has_value "$(bashio::services 'mqtt')"; then
    MQTT_USER="$(bashio::services 'mqtt' 'username')"
    MQTT_PASSWORD="$(bashio::services 'mqtt' 'password')"
    bashio::log.info "Using internal Home Assistant MQTT service."
elif ! bashio::config.is_empty 'mqtt_username'; then
    MQTT_USER=$(bashio::config 'mqtt_username')
    MQTT_PASSWORD=$(bashio::config 'mqtt_pw')
    bashio::log.info "Using manual MQTT configuration."
else
    bashio::log.error "No MQTT credentials found! Please start the Mosquitto Add-on."
    exit 1
fi

# --- DEVICE HANDLING ---
if [ "$INPUT_TYPE" = "serial" ]; then
    bashio::log.info "Looking for GPS Device: ${DEVICE}"

    count=0
    while [ ! -e "${DEVICE}" ] && [ $count -lt 30 ]; do
        sleep 1
        count=$((count+1))
    done

    if [ ! -e "${DEVICE}" ]; then
        bashio::log.error "GPS Device not found after 30 seconds."
        exit 1
    fi

    bashio::log.info "Device found. Setting baudrate to ${BAUDRATE}..."
    # Attempt stty but don't fail the script if it complains about permissions
    stty -F ${DEVICE} speed ${BAUDRATE} cs8 -cstopb -parenb raw 2>/dev/null || true

    bashio::log.info "Starting GPSD..."
    # Launch GPSD in background
    /usr/sbin/gpsd ${GPSD_OPTIONS} -F ${GPSD_SOCKET} -s ${BAUDRATE} ${DEVICE}

elif [ "$INPUT_TYPE" = "tcp" ]; then
    TCP_HOST=$(bashio::config 'tcp_host')
    TCP_PORT=$(bashio::config 'tcp_port')
    bashio::log.info "Starting GPSD via TCP..."
    /usr/sbin/gpsd ${GPSD_OPTIONS} -F ${GPSD_SOCKET} tcp://${TCP_HOST}:${TCP_PORT}
fi

# Wait a moment for GPSD to stabilize
sleep 2

# --- LAUNCH PYTHON BRIDGE ---
bashio::log.info "Starting MQTT Bridge..."
python3 /gpsd2mqtt.py "${MQTT_USER}" "${MQTT_PASSWORD}"
