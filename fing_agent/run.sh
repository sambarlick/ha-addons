#!/usr/bin/env bash
set -e
echo "[Fing Agent] Starting add-on v0.2.0..."

# Check that we're on Alpine, as expected by this new build method
if [ -f /etc/alpine-release ]; then
    echo "[Fing Agent] Running on Alpine, as expected."
else
    echo "[Fing Agent] WARNING: Not running on Alpine. This is unexpected."
fi

# This path is based on all our previous searches.
# It *must* exist now because we copied it in the Dockerfile.
AGENT_PATH="/usr/local/FingAgent/bin/fingagent"

echo "[Fing Agent] Checking for agent at ${AGENT_PATH}..."
if [ ! -f "${AGENT_PATH}" ]; then
    echo "[Fing Agent] FATAL: File not found at ${AGENT_PATH}."
    echo "The multi-stage build copy failed or the path is wrong."
    echo "--- Listing /usr/local/ ---"
    ls -la /usr/local/
    echo "--- Listing /usr/local/FingAgent/ (if it exists) ---"
    ls -la /usr/local/FingAgent/ || echo "/usr/local/FingAgent/ not found."
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
