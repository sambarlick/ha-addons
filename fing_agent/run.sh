#!/usr/bin/env bash
set -e
echo "[Fing Agent] Starting add-on v0.2.19..."
echo "[Fing Agent] This is now running INSIDE the official container."

# --- Path Definitions ---
AGENT_DIR="/usr/local/FingAgent"
AGENT_EXE="fingagent"
AGENT_PATH="${AGENT_DIR}/${AGENT_EXE}"
FING_DATA_DIR="/app/fingdata"
HA_DATA_DIR="/data" # This is where HA maps our 'data:rw'

echo "[Fing Agent] Checking for agent at ${AGENT_PATH}..."
if [ ! -f "${AGENT_PATH}" ]; then
    echo "[Fing Agent] FATAL: File not found at ${AGENT_PATH}."
    exit 1
fi

# --- Symlink Creation ---
echo "[Fing Agent] Ensuring parent directory /app exists..."
mkdir -p /app
echo "[Fing Agent] Creating symlink from ${HA_DATA_DIR} to ${FING_DATA_DIR}..."
ln -sfn "${HA_DATA_DIR}" "${FING_DATA_DIR}"

# --- Change Directory ---
echo "[Fing Agent] Changing working directory to ${AGENT_DIR}..."
cd "${AGENT_DIR}"

# --- Execute ---
echo "[Fing Agent] Found agent. Starting..."
exec "./${AGENT_EXE}"
