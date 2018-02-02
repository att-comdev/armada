#!/bin/bash
clean_container(){
    echo "Destroying $1 container..."
    docker stop $1 >/dev/null
    docker rm $1 >/dev/null
    echo "...container destroyed"
}

readlink(){
    (
    cd $(dirname $1)
    echo $PWD/$(basename $1)
    )
}

# Check to see if the aramada container exists
if [ -n "$( sudo docker ps -a | grep quay.io/attcomdev/armada )" ]; then
    echo "Armada container already exists..."
    clean_container armada
fi

# Check to see if the user is trying to apply a chart
if [ $1 = "apply" ]; then
    # TODO Handle erroneous or missing inputs
    # Bring up a new armada container with passed in yaml mounted to the container
    echo "Creating an Armada container..."
    docker run -d --net host -p 8000:8000 --name armada -v $(readlink $(dirname $2)):$(readlink $(dirname $2)) -v ~/.kube/config:/armada/.kube/config -v ~/.kube/plugins/armada/examples/:/examples quay.io/attcomdev/armada:latest
    docker exec armada armada apply $(readlink $2)
else
    # For any other command the chart does not need to be mounted to the container
    # Bring up a new armada container
    echo "Creating an Armada container..."
    docker run -d --net host -p 8000:8000 --name armada -v ~/.kube/config:/armada/.kube/config -v ~/.kube/plugins/armada/examples/:/examples quay.io/attcomdev/armada:latest
    docker exec armada armada "$@"
fi
clean_container armada
