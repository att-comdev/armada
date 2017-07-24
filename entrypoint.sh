#!/bin/bash

CMD="armada"
PORT="8000"

set -e

if [ "$1" = 'server' ]; then
    exec uwsgi --http :${PORT} --paste config:$(pwd)/etc/armada/api-paste.ini --enable-threads -L --pyargv " --config-file $(pwd)/etc/armada/armada.conf"
fi

if [ "$1" = 'tiller' ] || [ "$1" = 'apply' ]; then
    exec $CMD "$@"
fi

exec "$@"
