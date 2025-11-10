# This $BUILD_FROM will be "fing/fing-agent:latest"
# thanks to our build.json file.
ARG BUILD_FROM
FROM ${BUILD_FROM}

# The base image doesn't have bash, curl, jq, etc.
# and we don't need them!
#
# We just need to copy our run script and make it executable.
COPY run.sh /run.sh
RUN chmod a+x /run.sh

# This CMD overrides any default CMD in the base image
# and runs our script instead.
CMD [ "/run.sh" ]
