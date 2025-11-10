# --- Global Build Args ---
ARG BUILD_FROM

# --- Stage 1: The Fing Files ---
FROM fing/fing-agent:latest AS fing_files

# --- Stage 2: The Home Assistant Add-on ---
FROM ${BUILD_FROM}

# --- THIS IS THE FIX ---
# Installing the correct GNU compatibility library.
# The package is 'gcompat', not 'libgcompat'.
RUN apk add --no-cache libc6-compat gcompat

# --- Copy The Files ---
COPY --from=fing_files /usr/local/ /usr/local/

# Copy our startup script (run.sh)
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
