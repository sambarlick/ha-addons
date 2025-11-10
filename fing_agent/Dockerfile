# This $BUILD_FROM will now be "fing/fing-agent:latest"
# thanks to our new build.json file.
ARG BUILD_FROM
FROM ${BUILD_FROM}

# --- THIS IS THE FIX ---
# We are now inside the Debian container.
# We will install the Home Assistant 'bashio' library.
# We need 'curl' and 'jq' to do it.
RUN \
    apt-get update && \
    apt-get install -y curl jq && \
    # Install bashio
    curl -L "https://github.com/hassio-addons/bashio/raw/master/installer.sh" | bash

# --- Copy our startup script ---
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
