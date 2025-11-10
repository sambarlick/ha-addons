# This $BUILD_FROM will be "fing/fing-agent:latest"
# thanks to our build.json file.
ARG BUILD_FROM
FROM ${BUILD_FROM}

# --- THIS IS THE FIX ---
# We are now inside the Debian container.
# We will install the Home Assistant 'bashio' library.
RUN \
    apt-get update && \
    apt-get install -y curl jq && \
    # Install bashio (using the correct 'main' branch)
    curl -L "https://github.com/hassio-addons/bashio/raw/main/installer.sh" | bash

# --- Copy our startup script ---
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
