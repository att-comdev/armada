***********
Development
***********

Docker
######

To use the docker containter to develop:

1. Fork the `Repository <http://github.com/att-comdev/armada>`_
2. Clone the forked repo
3. Change to the directory of the cloned repo

.. code-block:: bash

    CURRENT_COMMIT=$(git log --pretty=format:'%h' -n 1)
    docker build . --file ./Dockerfile-requirements --tag armada-requirements:${CURRENT_COMMIT}
    docker run -d -P --name armada-requirements-${CURRENT_COMMIT} armada-requirements:${CURRENT_COMMIT} "python -m SimpleHTTPServer 8000"
    REQUIREMENTS_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' armada-requirements-${CURRENT_COMMIT})
    docker build . --file ./Dockerfile --tag armada:${CURRENT_COMMIT} --build-arg WHEELS_URL="http://${REQUIREMENTS_IP}:8000/wheels.tar.gz"
    docker rm -f armada-requirements-${CURRENT_COMMIT}
    docker run -d --name armada -v ~/.kube/config:/var/lib/armada/.kube/config:ro -v $(pwd)/examples/:/examples armada:${CURRENT_COMMIT}

.. note::

    The first build will take a little while. Afterwords, it will build much
    faster.

Virtualenv
##########

To use VirtualEnv we will need to add some extra steps

1. virtualenv venv
2. source ./venv/bin/activate
3. sudo sh ./tools/libgit2.sh

Test that it worked with:

.. code-block:: bash

    python -c 'import pygit2'

From the directory of the forked repository:

.. code-block:: bash

    pip install -r requirements.txt
    pip install -r test-requirements.txt
    pip install -e .

.. note::

    this will install the latest libgit2 library so you have to make sure you
    install the same version library with pip ( current version: 0.25.0 )

Kubernetes
##########

To test your armada fixes/features you will need to set-up a Kubernetes cluster.

We recommend:

`Kubeadm <https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/>`_

`Kubeadm-AIO <https://github.com/openstack/openstack-helm/tree/master/tools/kubeadm-aio>`_
