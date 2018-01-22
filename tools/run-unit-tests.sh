#!/usr/bin/env bash

# Script for passing regex filtering of unit tests to py.test conditionally.
# Needed because tox currently doesn't support conditional logic like this.

posargs=$@
if [ ${#posargs} -ge 1 ]; then
    py.test -vvv -s --ignore=hapi -k $1
else
    py.test -vvv -s --ignore=hapi
fi
TEST_STATUS=$?
set -e

exit $TEST_STATUS
