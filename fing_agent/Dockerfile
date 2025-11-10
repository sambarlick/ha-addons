# This ARG is provided by Home Assistant's builder.
# Thanks to our new config.yaml, this will be "fing/fing-agent:latest"
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Copy our startup script into the container
COPY run.sh /
RUN chmod a+x /run.sh

# Tell the container to run our script on start
CMD [ "/run.sh"
]
