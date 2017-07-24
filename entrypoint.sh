#!/bin/bash

CMD="armada"
PORT="8000"

set -e

if [ "$1" = 'server' ]; then
    gunicorn server:api -b :$PORT --chdir armada/api
fi

if [ "$1" = 'tiller' ] || [ "$1" = 'apply' ]; then
    exec $CMD "$@"
fi

exec "$@"
