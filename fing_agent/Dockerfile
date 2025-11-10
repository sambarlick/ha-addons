# --- Global Build Args ---
ARG BUILD_FROM

# --- Stage 1: The Fing Files ---
FROM fing/fing-agent:latest AS fing_files

# --- Stage 2: The Home Assistant Add-on ---
FROM ${BUILD_FROM}

# --- Install Alpine-native libraries ---
# We need all the libraries the agent *would* have used
RUN apk add --no-cache libc6-compat gcompat libstdc++ boost

# --- Copy The Fing Agent Files ---
COPY --from=fing_files /usr/local/ /usr/local/

# --- THIS IS THE FIX ---
# Delete the Debian-compiled libboost libraries we just copied.
# This will force the agent to fall back to the Alpine-native
# boost libraries we installed with 'apk add'.
RUN rm -f /usr/local/FingAgent/lib/libboost*

# --- Copy our startup script ---
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
