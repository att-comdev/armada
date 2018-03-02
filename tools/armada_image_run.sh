#!/bin/bash
#
# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -x

# Create container
docker run \
  -v $(pwd)/etc:/etc \
	-d \
	--name armada-api-test \
	-p 127.0.0.1:8000:8000 \
	$IMAGE \
	server

# Verify container was successfully created
# If not successfull, print out logs
GOOD="HTTP/1.1 204 No Content"
if curl\
	-m 5 \
	-v \
	--silent \
	127.0.0.1:8000/api/v1.0/health \
	--stderr - \
	| grep "$GOOD"
then
	echo "Health Check Complete";
else
	echo "Failed Health Check";
	docker logs armada-api-test
fi

# Remove container
docker rm -fv armada-api-test
