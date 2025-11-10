# --- Global Build Args ---
ARG BUILD_FROM

# --- Stage 1: The Fing Files ---
FROM fing/fing-agent:latest AS fing_files

# --- Stage 2: The Home Assistant Add-on ---
FROM ${BUILD_FROM}

# --- THIS IS THE FIX ---
# Install the missing Debian/Ubuntu compatibility libraries
# libc6-compat (for basic C libraries)
# libstdc++ (for C++ libraries)
# libintl (for C++ localization/internationalization libraries)
RUN apk add --no-cache libc6-compat libstdc++ libintl

# --- Copy The Files ---
COPY --from=fing_files /usr/local/ /usr/local/

# Copy our startup script (run.sh)
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
