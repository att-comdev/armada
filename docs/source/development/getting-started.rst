***********
Development
***********

Docker
######

To use the docker containter to develop:

1. Fork the `Repository <http://github.com/att-comdev/armada>`_
2. Clone the forked repo

.. code-block:: bash

    cd armada
    export repo="https://github.com/<forked-repo>/armada.git"
    export branch="<branch>"

    docker build . -t quay.io/attcomdev/armada:latest --build-arg REPO=$repo --build-arg VERSION=$branch

    docker run -d --name armada -v ~/.kube/config:/root/.kube/config -v $(pwd)/examples/:/examples quay.io/attcomdev/armada:latest

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
