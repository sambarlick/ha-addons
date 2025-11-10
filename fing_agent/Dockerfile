# This $BUILD_FROM will be "fing/fing-agent:latest"
# thanks to our build.json file.
ARG BUILD_FROM
FROM ${BUILD_FROM}

# We are now inside the Debian container.
# We will install the Home Assistant 'bashio' library.
RUN \
    apt-get update && \
    apt-get install -y curl jq && \
    # --- THIS IS THE FIX ---
    # Using the correct, official installer URL
    curl -L "https://raw.githubusercontent.com/home-assistant/addons/master/bashio/installer.sh" | bash

# --- Copy our startup script ---
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
