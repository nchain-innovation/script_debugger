#!/bin/bash

docker run -it \
    --mount type=bind,source="$(pwd)/src",destination=/app/src \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --rm script_debugger \
    $1 $2
