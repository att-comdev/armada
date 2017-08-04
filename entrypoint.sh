#!/bin/bash

CMD="armada"
set -ex

if [ "$1" = 'server' ]; then
    exec gunicorn server:api -b :$PORT --chdir /opt/armada/armada/api
fi

if [ "$1" = 'tiller' ] || [ "$1" = 'apply' ]; then
    exec $CMD "$@"
fi

exec "$@"
