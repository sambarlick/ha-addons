#!/usr/bin/env bash
set -e # Exit on error

echo "[Fing Agent] Starting add-on..."

# --- FIX ---
# The error "ln: /app/fingdata: No such file or directory" means
# the parent directory /app does not exist in the base image.
# We must create it before we can create a symlink inside it.
echo "[Fing Agent] Ensuring parent directory /app exists..."
mkdir -p /app
# --- END FIX ---

# This logic handles if /app/fingdata somehow exists (e.g., on a rebuild)
# It moves any existing data to /data and removes the old directory
if [ -d "/app/fingdata" ] && [ ! -L "/app/fingdata" ]; then
  echo "[Fing Agent] Found existing /app/fingdata, moving contents to /data..."
  # Move all contents, including hidden files, ignore errors if empty
  mv /app/fingdata/* /data/ 2>/dev/null || true
  rm -rf /app/fingdata
fi

# Now, create the symlink.
# -s = symbolic, -f = force (overwrite), -n = no-dereference
# This links /data (the add-on's persistent storage)
# to /app/fingdata (where the Fing Agent expects it)
echo "[Fing Agent] Creating symlink from /data to /app/fingdata..."
ln -sfn /data /app/fingdata

echo "[Fing Agent] Starting the Fing Agent process..."

# 'exec' replaces this script with the agent process
exec /usr/local/FingAgent/bin/fingagent
