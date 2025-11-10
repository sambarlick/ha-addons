# This $BUILD_FROM will be "fing/fing-agent:latest"
ARG BUILD_FROM
FROM ${BUILD_FROM}

# --- Copy our s6-overlay script ---
# We copy our rootfs directory to the container's root
# This places our setup script in /etc/cont-init.d/
COPY rootfs /

# We do NOT add a CMD.
# We let the base image's s6 entrypoint run.
# It will automatically find and execute our 01-fing-setup.sh script
# before starting the main fingagent service.
