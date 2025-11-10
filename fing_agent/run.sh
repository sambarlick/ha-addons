#!/usr/bin/env bash
set -e # Exit on error

echo "[Fing Agent] Starting add-on v0.1.0..."

# --- Final OS Check ---
if [ -f /etc/debian_version ]; then
    echo "[Fing Agent] SUCCESS: Found /etc/debian_version. We are in the correct container."
else
    echo "[Fing Agent] FATAL: /etc/debian_version not found. Still in the wrong container."
    exit 1
fi

# --- Symlink Creation ---
echo "[Fing Agent] Ensuring parent directory /app exists..."
mkdir -p /app

echo "[Fing Agent] Creating symlink from /data to /app/fingdata..."
ln -sfn /data /app/fingdata

# --- Find and Execute ---
echo "[Fing Agent] Locating executable..."

# We will search the most likely paths for the agent
# This is robust and will find the file.
AGENT_PATH=$(find /usr/local/ -name "fingagent" 2>/dev/null || true)

if [ -z "${AGENT_PATH}" ]; then
  echo "[Fing Agent] FATAL: Could not find 'fingagent' in /usr/local/"
  echo "Please check the add-on logs."
  exit 1
fi

echo "[Fing Agent] Found agent at ${AGENT_PATH}. Starting..."
exec "${AGENT_PATH}"
