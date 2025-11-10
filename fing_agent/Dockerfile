# --- Global Build Args ---
# This MUST be at the top. This receives the HA builder's
# default base image (e.g., ghcr.io/home-assistant/aarch64-base:latest)
ARG BUILD_FROM

# --- Stage 1: The Fing Files ---
# Pull the official Fing agent image and name this stage 'fing_files'
FROM fing/fing-agent:latest AS fing_files

# --- Stage 2: The Home Assistant Add-on ---
# Now we use the global ARG.
FROM ${BUILD_FROM}

# --- Copy The Files ---
# Copy the /usr/local/ directory from Stage 1 into our Alpine container.
COPY --from=fing_files /usr/local/ /usr/local/

# Copy our startup script (run.sh)
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
