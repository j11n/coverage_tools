#!/bin/bash
#
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

podman run -i --security-opt label=disable \
    -v ${THIS_DIR}/..:/software \
    -v ${THIS_DIR}/..:/files \
    -t python_dev \
    /bin/bash

#    -t uhab_admin \
