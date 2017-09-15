#!/bin/bash

# Check to see if the aramada container exists
if [ -n "$( sudo docker ps -a | grep quay.io/attcomdev/armada )" ]; then
  echo "Armada container already exists..."
  docker exec armada armada "$@"
else
# If the container does not exist bring, bring one up for the user
  echo "Armada container does not exist..."
  echo "Creating an Armada container..."
  docker run -d --net host -p 8000:8000 --name armada -v ~/.kube/config:/armada/.kube/config -v ~/.kube/plugins/armada/examples/:/examples quay.io/attcomdev/armada:latest
  echo "...Armada container created"
  docker exec armada armada "$@"
fi
