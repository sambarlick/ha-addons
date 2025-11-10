# This $BUILD_FROM will be "fing/fing-agent:latest"
# thanks to our build.json file.
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set the latest bashio version
ENV BASHIO_VERSION=v0.17.2

# We are now inside the Debian container.
# We will install dependencies and the Home Assistant 'bashio' library.
RUN \
    apt-get update && \
    \
    # --- THIS IS THE FIX ---
    # The base image has broken dependencies.
    # Attempt to fix them *before* installing anything new.
    apt-get install -f -y && \
    apt-get --fix-broken install -y && \
    \
    # Now, install our required packages minimally
    # Use --no-install-recommends to avoid pulling in more conflicts
    apt-get install -y --no-install-recommends curl jq tar gzip && \
    \
    # --- Install Bashio ---
    mkdir -p /usr/src/bashio && \
    curl -L -f -s "https://github.com/hassio-addons/bashio/archive/${BASHIO_VERSION}.tar.gz" \
    | tar -xzf - --strip 1 -C /usr/src/bashio && \
    mv /usr/src/bashio/lib /usr/lib/bashio && \
    ln -s /usr/lib/bashio/bashio /usr/bin/bashio && \
    \
    # --- Clean up ---
    rm -rf /usr/src/bashio && \
    rm -rf /var/lib/apt/lists/*

# --- Copy our startup script ---
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
