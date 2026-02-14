#!/usr/bin/with-contenv bashio

# Get the device config
CONFIG_PATH="/data/options.json"
INPUT_TYPE=$(bashio::config 'input_type')
DEVICE=$(bashio::config 'device')
TCP_HOST=$(bashio::config 'tcp_host')
TCP_PORT=$(bashio::config 'tcp_port')
BAUDRATE=$(bashio::config 'baudrate' 9600)

# Use the -N flag to keep gpsd in the foreground if needed, 
# but since we run python after, background is fine.
# Added -n (don't wait) and -b (read-only) explicitly here for safety.
GPSD_OPTIONS=$(bashio::config 'gpsd_options') 
GPSD_OPTIONS="${GPSD_OPTIONS} -n -b -G" 

# Define the socket file explicitly so clients can find it
GPSD_SOCKET="/var/run/gpsd.sock"

CHARSIZE=$(bashio::config 'charsize' 8)
PARITY=$(bashio::config 'parity' false)
STOPBIT=$(bashio::config 'stopbit' 1)
CONTROL="clocal"
MQTT_USER=$(bashio::config 'mqtt_username')
MQTT_PASSWORD=$(bashio::config 'mqtt_pw')
HA_AUTH=false

# stty setup
if [ "$PARITY" = false ]; then
  PARITY_CL="-parenb"
elif [ "$PARITY" = true ]; then
  PARITY_CL="parenb"
fi

if [ "$STOPBIT" -eq 1 ]; then
  STOPBIT_CL="-cstopb"
elif [ "$STOPBIT" -eq 2 ]; then
  STOPBIT_CL="cstopb"
fi

# ----------------------------------------------------------------
# IMPROVEMENT 1: MQTT Auth Check
# ----------------------------------------------------------------
if bashio::config.is_empty 'mqtt_username' && bashio::var.has_value "$(bashio::services 'mqtt')"; then
    MQTT_USER="$(bashio::services 'mqtt' 'username')"
    MQTT_PASSWORD="$(bashio::services 'mqtt' 'password')"
    HA_AUTH=true
elif bashio::config.is_empty 'mqtt_username'; then
    bashio::log.error "No MQTT credentials found. Please configure them or install the Mosquitto Add-on."
    exit 1
fi

# ----------------------------------------------------------------
# IMPROVEMENT 2: The "Wait for Device" Loop (Vital for Caravans)
# ----------------------------------------------------------------
if [ "$INPUT_TYPE" = "serial" ]; then
    bashio::log.info "Waiting for GPS device: ${DEVICE}..."
    
    # Loop for up to 30 seconds waiting for the USB stick to appear
    count=0
    while [ ! -e "${DEVICE}" ] && [ $count -lt 30 ]; do
        sleep 1
        count=$((count+1))
    done

    if [ ! -e "${DEVICE}" ]; then
        bashio::log.error "Timeout! GPS device ${DEVICE} not found after 30 seconds."
        bashio::log.error "Please check if the USB stick is plugged in."
        exit 1
    fi

    bashio::log.info "Device found! Configuring serial port..."
    
    # Configure the port with stty
    # Added error suppression (2>/dev/null) just in case stty is fussy, 
    # but logging the attempt.
    /bin/stty -F ${DEVICE} raw ${BAUDRATE} cs${CHARSIZE} ${PARITY_CL} ${CONTROL} ${STOPBIT_CL} || bashio::log.warning "stty configuration had a minor issue, continuing anyway..."

    bashio::log.info "Starting GPSD..."
    /usr/sbin/gpsd --version
    
    # Passing socket (-F) explicitly is good practice
    /usr/sbin/gpsd ${GPSD_OPTIONS} -F ${GPSD_SOCKET} -s ${BAUDRATE} ${DEVICE}

elif [ "$INPUT_TYPE" = "tcp" ]; then
    if [ -z "$TCP_HOST" ] || [ -z "$TCP_PORT" ]; then
        bashio::log.error "TCP Host and Port must be defined for TCP mode."
        exit 1
    fi
    bashio::log.info "Starting GPSD with TCP source ${TCP_HOST}:${TCP_PORT} ..."
    /usr/sbin/gpsd ${GPSD_OPTIONS} -F ${GPSD_SOCKET} tcp://${TCP_HOST}:${TCP_PORT}
else
    bashio::log.error "Unknown input_type: $INPUT_TYPE"
    exit 1
fi

# ----------------------------------------------------------------
# IMPROVEMENT 3: Python Launcher
# ----------------------------------------------------------------
if [ $HA_AUTH = true ]; then
    bashio::log.info "Starting MQTT Publisher with Home Assistant credentials..."
else
    bashio::log.info "Starting MQTT Publisher with username ${MQTT_USER}..."
fi
    
# Launch the python script
python3 /gpsd2mqtt.py ${MQTT_USER} ${MQTT_PASSWORD}
