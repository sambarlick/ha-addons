# This $BUILD_FROM will be "fing/fing-agent:latest"
# thanks to our build.json file.
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set the latest bashio version
ENV BASHIO_VERSION=v0.17.2

# We are now inside the Debian container.
# Install dependencies and the Home Assistant 'bashio' library.
RUN \
    apt-get update && \
    apt-get install -y curl jq tar gzip && \
    \
    # --- This is the correct bashio installation method ---
    mkdir -p /usr/src/bashio && \
    curl -L -f -s "https://github.com/hassio-addons/bashio/archive/${BASHIO_VERSION}.tar.gz" \
    | tar -xzf - --strip 1 -C /usr/src/bashio && \
    mv /usr/src/bashio/lib /usr/lib/bashio && \
    ln -s /usr/lib/bashio/bashio /usr/bin/bashio

# --- Copy our startup script ---
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
