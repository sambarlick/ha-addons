# --- Global Build Args ---
ARG BUILD_FROM

# --- Stage 1: The Fing Files ---
FROM fing/fing-agent:latest AS fing_files

# --- Stage 2: The Home Assistant Add-on ---
FROM ${BUILD_FROM}

# --- THIS IS THE DATA-DRIVEN FIX ---
# Install all known dependencies, mapped to their Alpine names
RUN apk add --no-cache \
    libc6-compat \
    gcompat \
    libstdc++ \
    libintl \
    openssl3 \
    protobuf-c \
    zlib \
    lz4-libs \
    zstd-libs

# --- Copy The Files ---
# We copy EVERYTHING and delete NOTHING
COPY --from=fing_files /usr/local/ /usr/local/

# --- Copy our startup script ---
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
