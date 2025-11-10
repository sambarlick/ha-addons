#!/usr/bin/env bash
set -e
echo "[Fing Agent] Starting add-on v0.2.2..."

# --- Path Definition ---
# The log from 0.2.1 (logs-8.txt) proved the path is
# NOT in the /bin/ subfolder, but in the root of FingAgent.
AGENT_PATH="/usr/local/FingAgent/fingagent"

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

# --- Execute ---
echo "[Fing Agent] Found agent. Starting..."
exec "${AGENT_PATH}"
