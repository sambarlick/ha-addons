#!/usr/bin/env bash
set -e # Exit on error

echo "[Fing Agent] Starting DIAGNOSTIC script v2..."

echo "--- Listing / (root) ---"
ls -la /

echo "--- Listing /usr/bin/ (looking for 'fing') ---"
ls -la /usr/bin/ | grep 'fing' || echo "No 'fing' files found in /usr/bin/."

echo "--- Listing /opt/ ---"
ls -la /opt/ || echo "Folder /opt/ not found."

echo "--- Searching ALL directories for 'fingagent' (this may take longer)... ---"
# Find any file named 'fingagent' starting from /
# The 2>/dev/null hides 'Permission denied' errors for a cleaner log
find / -name "fingagent" 2>/dev/null || echo "find 'fingagent' failed"

echo "--- Searching ALL directories for 'fing-agent' (with hyphen)... ---"
find / -name "fing-agent" 2>/dev/null || echo "find 'fing-agent' failed"

echo "--- DIAGNOSTIC SCRIPT V2 COMPLETE ---"
echo "--- Please copy the log above and paste it in our chat. ---"
echo "--- The add-on will now stop, which is expected. ---"

# The script will now end, and the container will stop. This is correct.
