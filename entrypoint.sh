#!/bin/bash

CMD="armada"
PORT="8000"

set -e

if [ "$1" = 'server' ]; then
    exec uwsgi --http :${PORT} --honour-stdin --http-timeout 3600 --paste config:/etc/armada/api-paste.ini --enable-threads -L --pyargv "--config-file /etc/armada/armada.conf"
else
    exec $CMD "$@"
fi
