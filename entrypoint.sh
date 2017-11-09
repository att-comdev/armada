#!/bin/bash

CMD="armada"
PORT="8000"

set -e

if [ "$1" = 'test' ]; then
    exec ./armada/tests/functional/client-armada.sh
fi

if [ "$1" = 'server' ]; then
    exec uwsgi --http :${PORT} --http-timeout 3600 --paste config:/etc/armada/api-paste.ini --enable-threads -L
else
    exec $CMD "$@"
fi

