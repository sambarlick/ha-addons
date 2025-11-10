#!/usr/bin/env bash
set -e # Exit on error

echo "[Fing Agent] Starting DIAGNOSTIC script..."

echo "--- Listing /usr/local/ ---"
ls -la /usr/local/

echo "--- Listing /usr/local/FingAgent/ ---"
# This might fail if the folder doesn't exist, which is good info
ls -la /usr/local/FingAgent/ || echo "Folder /usr/local/FingAgent/ not found."

echo "--- Listing /usr/local/FingAgent/bin/ ---"
# This might also fail, which is also good info
ls -la /usr/local/FingAgent/bin/ || echo "Folder /usr/local/FingAgent/bin/ not found."

echo "--- Searching for 'fingagent' executable (this may take a moment)... ---"
# Find any file named 'fingagent' starting from /usr/local
find /usr/local/ -name "fingagent"

echo "--- DIAGNOSTIC SCRIPT COMPLETE ---"
echo "--- Please copy the log above and paste it in our chat. ---"
echo "--- The add-on will now stop, which is expected. ---"

# We are not running the agent, so the script will end, and s6 will stop.
# This is 100% expected.
