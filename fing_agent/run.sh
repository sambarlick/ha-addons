#!/usr/bin/env bash
set -e # Exit on error

echo "[Fing Agent] Starting DIAGNOSTIC script v5 (Version 0.0.8)..."
echo "--- This script will test if the new Dockerfile 'FROM' directive worked. ---"

echo "--- Test 1: Checking container OS ---"
if [ -f /etc/alpine-release ]; then
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! FAILURE: Found /etc/alpine-release."
    echo "!! The fix did not work. It is still the Alpine image."
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    cat /etc/alpine-release
elif [ -f /etc/debian_version ]; then
    echo "=========================================================="
    echo "== SUCCESS: Found /etc/debian_version."
    echo "== This IS the correct Debian-based fing/fing-agent image."
    echo "== Now... let's find that file."
    echo "=========================================================="
    cat /etc/debian_version
else
    echo "!! UNKNOWN: Neither /etc/alpine-release nor /etc/debian_version was found."
fi

echo "--- Test 2: Searching ALL directories for ANY file with 'fing' in the name... ---"
# 2>/dev/null hides 'Permission denied' errors for a cleaner log
find / -name "*fing*" 2>/dev/null || echo "No files with 'fing' in the name found."

echo "--- DIAGNOSTIC SCRIPT V5 COMPLETE ---"
echo "--- The add-on will now stop, which is expected. -
--"
