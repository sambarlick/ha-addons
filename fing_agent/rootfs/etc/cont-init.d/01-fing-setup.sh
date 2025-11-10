#!/bin/sh
set -e

echo "[Fing Init] Preparing environment..."

# --- Path Definitions ---
AGENT_DIR="/usr/local/FingAgent"
FING_DATA_DIR="/app/fingdata"
HA_DATA_DIR="/data"

# --- Symlink Creation ---
echo "[Fing Init] Ensuring parent directory /app exists..."
mkdir -p /app
echo "[Fing Init] Linking HA data dir (${HA_DATA_DIR}) to Fing data dir (${FING_DATA_DIR})..."
ln -sfn "${HA_DATA_DIR}" "${FING_DATA_DIR}"

# --- Environment Setup (THE FIX) ---
# We set these variables here, and the s6-overlay
# will pass them to the main fing agent service.

export LD_LIBRARY_PATH="${AGENT_DIR}/lib"
echo "[Fing Init] Set LD_LIBRARY_PATH"

export FING_DATA_DIR="${FING_DATA_DIR}"
echo "[Fing Init] Set FING_DATA_DIR"

echo "[Fing Init] Environment setup complete. Handing over to s6..."
