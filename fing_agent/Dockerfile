# --- Global Build Args ---
ARG BUILD_FROM

# --- Stage 1: The Fing Files ---
FROM fing/fing-agent:latest AS fing_files

# --- Stage 2: The Home Assistant Add-on ---
FROM ${BUILD_FROM}

# --- THIS IS THE "KITCHEN SINK" FIX ---
# Install ALL compatibility libraries at once:
# libc6-compat: Basic C library compatibility
# gcompat: Fuller C library (glibc) compatibility
# libstdc++: The C++ standard library
# libintl: The C++ localization library (for the libboost_locale error)
RUN apk add --no-cache libc6-compat gcompat libstdc++ libintl

# --- Copy The Files ---
# We copy EVERYTHING and delete NOTHING
COPY --from=fing_files /usr/local/ /usr/local/

# --- Copy our startup script ---
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
