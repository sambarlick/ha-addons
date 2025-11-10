# This $BUILD_FROM will be "fing/fing-agent:latest"
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Copy our startup script
COPY run.sh /run.sh

# Make it executable (this is correct)
RUN chmod a+x /run.sh

# Tell the container to run our script instead of its default
CMD [ "/run.sh" ]
