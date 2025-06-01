#!/bin/bash
xhost +local:root

docker run -it --rm \
    --net host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/examples:/app/examples \
    pyside6-minimal