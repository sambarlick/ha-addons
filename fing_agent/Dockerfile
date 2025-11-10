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
    # Add tar and gzip to install the bashio release
    apt-get install -y curl jq tar gzip && \
    \
    # --- THIS IS THE FIX ---
    # Download and extract the bashio release tarball
    mkdir -p /usr/src/bashio && \
    curl -L -f -s "https://github.com/hassio-addons/bashio/archive/${BASHIO_VERSION}.tar.gz" \
    | tar -xzf - --strip 1 -C /usr/src/bashio && \
    \
    # Move the library files to the correct location
    mv /usr/src/bashio/lib /usr/lib/bashio && \
    \
    # Create the symlink so scripts can find 'bashio'
    ln -s /usr/lib/bashio/bashio /usr/bin/bashio && \
    \
    # Clean up
    rm -rf /usr/src/bashio && \
    apt-get purge -y --auto-remove tar gzip

# --- Copy our startup script ---
COPY run.sh /
RUN chmod a+x /run.sh

# Run our script
CMD [ "/run.sh" ]
