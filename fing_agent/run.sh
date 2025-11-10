#!/usr/bin/env bash
set -e # Exit on error

echo "[Fing Agent] Starting add-on..."

# The Fing container expects its data at /app/fingdata
# The Home Assistant add-on provides persistent data at /data
# We create a symlink to bridge this gap.

# Ensure the target directory exists (it's part of the base image)
if [ -d "/app/fingdata" ]; then
  # If it's a directory but not a symlink, move its contents
  if [ ! -L "/app/fingdata" ]; then
    echo "[Fing Agent] Moving existing /app/fingdata contents to /data..."
    # Move all contents, including hidden files, ignore errors if empty
    mv /app/fingdata/* /data/ 2>/dev/null || true
    rm -rf /app/fingdata
  fi
fi

# Create the symlink
# -s = symbolic, -f = force (overwrite), -n = no-dereference
ln -sfn /data /app/fingdata

echo "[Fing Agent] Starting the Fing Agent process..."

# 'exec' replaces this script with the agent process
# This is the original entrypoint/cmd of the base image
exec /usr/bin/fing-agent
