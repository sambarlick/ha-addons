#!/bin/sh
set -e

echo "[Fing Agent] Starting add-on (run.sh v2)..."

# --- Path Definitions ---
AGENT_DIR="/usr/local/FingAgent"
AGENT_EXE="fingagent"
FING_DATA_DIR="/app/fingdata"
HA_DATA_DIR="/data" # This is where HA maps our 'data:rw'

# --- Symlink Creation ---
echo "[Fing Agent] Ensuring parent directory /app exists..."
mkdir -p /app
echo "[Fing Agent] Linking HA data dir (${HA_DATA_DIR}) to Fing data dir (${FING_DATA_DIR})..."
ln -sfn "${HA_DATA_DIR}" "${FING_DATA_DIR}"

# --- Environment Setup (THE REAL FIXES) ---

# --- FIX 1: LD_LIBRARY_PATH ---
# Force the agent to use *only* its own bundled libraries.
# This line is the fix for all 'Error relocating' messages.
export LD_LIBRARY_PATH="${AGENT_DIR}/lib"
echo "[Fing Agent] Set LD_LIBRARY_PATH to: ${LD_LIBRARY_PATH}"

# --- FIX 2: FING_DATA_DIR ---
# Tell the agent where its data directory is to fix the warning
export FING_DATA_DIR="${FING_DATA_DIR}"
echo "[Fing Agent] Set FING_DATA_DIR to: ${FING_DATA_DIR}"

# --- Change Directory ---
echo "[Fing Agent] Changing working directory to ${AGENT_DIR}..."
cd "${AGENT_DIR}"

# --- Execute ---
echo "[Fing Agent] Found agent. Starting..."
exec "./${AGENT_EXE}"
