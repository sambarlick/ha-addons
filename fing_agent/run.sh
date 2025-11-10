#!/usr/bin/env bash
set -e # Exit on error

echo "[Fing Agent] Starting DIAGNOSTIC script v3..."

echo "--- Listing /usr/bin/ (looking for 'fing') ---"
ls -la /usr/bin/ | grep 'fing' || echo "No 'fing' files found in /usr/bin/."

echo "--- Listing /usr/local/bin/ (looking for 'fing') ---"
ls -la /usr/local/bin/ | grep 'fing' || echo "/usr/local/bin/ not found or no 'fing' files."

echo "--- Listing /bin/ (looking for 'fing') ---"
ls -la /bin/ | grep 'fing' || echo "No 'fing' files found in /bin/."

echo "--- Searching ALL directories for ANY file with 'fing' in the name... ---"
# This is the important one. It will find 'fingagent', 'fing', 'fing.sh', etc.
# 2>/dev/null hides 'Permission denied' errors for a cleaner log
find / -name "*fing*" 2>/dev/null || echo "No files with 'fing' in the name found."

echo "--- DIAGNOSTIC SCRIPT V3 COMPLETE ---"
echo "--- Please copy the log above and paste it in our chat. ---"
echo "--- The add-on will now stop, which is expected. ---"

# The script will now end, and the container will stop. This is c
orrect.
