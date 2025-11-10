#!/usr/bin/env bash
set -e
echo "[Fing Agent] Starting add-on v0.2.14..."

# --- Path Definitions ---
AGENT_DIR="/usr/local/FingAgent"
AGENT_EXE="fingagent"
AGENT_PATH="${AGENT_DIR}/${AGENT_EXE}"
SYSTEM_LIB_PATH="/usr/lib"

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
# Force the linker to ONLY use the Alpine system libraries.
export LD_LIBRARY_PATH="${SYSTEM_LIB_PATH}"
echo "[Fing Agent] Set LD_LIBRARY_PATH to: ${LD_LIBRARY_PATH}"

# --- Change Directory ---
echo "[Fing Agent] Changing working directory to ${AGENT_DIR}..."
cd "${AGENT_DIR}"

# --- Execute ---
echo "[Fing Agent] Found agent. Starting..."
exec "./${AGENT_EXE}"
