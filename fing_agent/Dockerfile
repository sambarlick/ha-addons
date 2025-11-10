# --- Stage 1: The Fing Files ---
# Pull the official Fing agent image and name this stage 'fing_files'
# This is the Debian image with all the real files.
FROM fing/fing-agent:latest AS fing_files

# --- Stage 2: The Home Assistant Add-on ---
# This is the standard HA Alpine base image, injected by the builder
ARG BUILD_FROM
FROM ${BUILD_FROM}

# --- Copy The Files ---
# This is the magic. We copy the entire /usr/local/ directory
# from Stage 1 (fing_files) into our new Alpine container. This brings
# /usr/local/FingAgent/ and all its files with it.
COPY --from=fing_files /usr/local/ /usr/local/

# Copy our startup script (run.sh)
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
