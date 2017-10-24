#!/bin/bash

set -ex
export HOME=/tmp

# Extract the DB string from deckhand.conf and get the
# value of the DB host and port
db_string=`grep -i '^connection =' ${DECKHAND_CONFIG_FILE}`
db_fqdn=`echo ${db_string#*@} | cut -f1 -d"."`
db_port=`echo ${db_string#*@} | grep -o "[0-9]\+"`

pgsql_superuser_cmd () {
  DB_COMMAND="$1"
  if [[ ! -z $2 ]]; then
      EXPORT PGDATABASE=$2
  fi

  psql \
  -h $db_fqdn \
  -p $db_port \
  -U ${ROOT_DB_USER} \
  --command="${DB_COMMAND}"
}

# Create db
pgsql_superuser_cmd "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || pgsql_superuser_cmd "CREATE DATABASE $DB_NAME"

# Create db user
pgsql_superuser_cmd "SELECT * FROM pg_roles WHERE rolname = '$DB_USER';" | tail -n +3 | head -n -2 | grep -q 1 || \
    pgsql_superuser_cmd "CREATE ROLE ${DB_USER} LOGIN PASSWORD '$DB_PASS';" && pgsql_superuser_cmd "ALTER USER ${DB_USER} WITH SUPERUSER"

# Grant permissions to user
pgsql_superuser_cmd "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to $DB_USER;"
