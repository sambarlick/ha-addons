# Changelog

## 1.0.3
- Added `SYS_ADMIN` to privileged flags to allow agent to start and stay running.

## 1.0.2
- Corrected the `fingagent` executable path in `run.sh` to `/usr/local/FingAgent/fingagent`.

## 1.0.1
- Fixed startup bug by adding `mkdir -p /app` to `run.sh` before creating symlink.
- Initial public release.
