# This is the fix. We are no longer using the HA build arg.
# We are explicitly pulling the multi-arch 'fing/fing-agent' image.
FROM fing/fing-agent:latest

# Copy our startup script into the container
COPY run.sh /
RUN chmod a+x /run.sh

# Tell the container to run our script on start
CMD [ "/run.sh" ]
