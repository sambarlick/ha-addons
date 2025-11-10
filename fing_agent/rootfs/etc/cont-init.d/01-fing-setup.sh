#!/bin/sh
set -e

echo "[Fing Init] Preparing environment..."

# --- Path Definitions ---
AGENT_DIR="/usr/local/FingAgent"
FING_DATA_DIR="/app/fingdata"
HA_DATA_DIR="/data"
S6_ENV_DIR="/var/run/s6/container_environment"

# --- Symlink Creation ---
echo "[Fing Init] Ensuring parent directory /app exists..."
mkdir -p /app
echo "[Fing Init] Linking HA data dir (${HA_DATA_DIR}) to Fing data dir (${FING_DATA_DIR})..."
ln -sfn "${HA_DATA_DIR}" "${FING_DATA_DIR}"

# --- Environment Setup (THE REAL FIX) ---
# Don't use 'export'. We must write the variable content
# to a file inside the s6 environment directory.

echo "[Fing Init] Setting LD_LIBRARY_PATH for s6..."
echo -n "${AGENT_DIR}/lib" > "${S6_ENV_DIR}/LD_LIBRARY_PATH"

echo "[Fing Init] Setting FING_DATA_DIR for s6..."
echo -n "${FING_DATA_DIR}" > "${S6_ENV_DIR}/FING_DATA_DIR"

echo "[Fing Init] Environment setup complete. Handing over to s6..."
