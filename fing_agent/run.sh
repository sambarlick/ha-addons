#!/usr/bin/env bash
set -e
echo "[Fing Agent] Starting add-on v0.2.9..."

# --- Path Definitions ---
AGENT_DIR="/usr/local/FingAgent"
AGENT_EXE="fingagent"
AGENT_PATH="${AGENT_DIR}/${AGENT_EXE}"
AGENT_LIB_PATH="${AGENT_DIR}/lib"
SYSTEM_LIB_PATH="/usr/lib" # Standard Alpine lib path

echo "[Fing Agent] Checking for agent at ${AGENT_PATH}..."
if [ ! -f "${AGENT_PATH}" ]; then
    echo "[Fing Agent] FATAL: File not found at ${AGENT_PATH}."
    exit 1
fi

# --- Symlink Creation ---
echo "[Fing Agent] Ensuring parent directory /app exists..."
mkdir -p /app
echo "[Fing Agent] Creating symlink from /data to /app/fingdata..."
ln -sfn /data /app/fingdata

# --- THIS IS THE FIX ---
# Set the LD_LIBRARY_PATH to tell the linker to look in
# the agent's own lib folder AND the standard system lib folder.
export LD_LIBRARY_PATH="${AGENT_LIB_PATH}:${SYSTEM_LIB_PATH}"
echo "[Fing Agent] Set LD_LIBRARY_PATH to: ${LD_LIBRARY_PATH}"

# --- Change Directory ---
echo "[Fing Agent] Changing working directory to ${AGENT_DIR}..."
cd "${AGENT_DIR}"

# --- Execute ---
echo "[Fing Agent] Found agent. Starting..."
exec "./${AGENT_EXE}"
