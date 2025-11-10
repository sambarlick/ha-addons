# --- Global Build Args ---
ARG BUILD_FROM

# --- Stage 1: The Fing Files ---
FROM fing/fing-agent:latest AS fing_files

# --- Stage 2: The Home Assistant Add-on ---
FROM ${BUILD_FROM}

# --- Install Alpine-native libraries ---
# We install all the Alpine-native versions of the libraries.
RUN apk add --no-cache libc6-compat gcompat libstdc++ boost

# --- Copy The Fing Agent Files ---
COPY --from=fing_files /usr/local/ /usr/local/

# --- THIS IS THE FIX ---
# Delete ALL the Debian-compiled libraries we just copied.
# This forces the agent to use the Alpine-native ones from /usr/lib.
RUN rm -f /usr/local/FingAgent/lib/*.so*

# --- Copy our startup script ---
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
