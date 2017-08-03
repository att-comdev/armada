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

    git clone http://github.com/att-comdev/armada.git 
    cd armada

    tox -e genconfig
    tox -e genpolicy

    docker build . -t armada:local

    docker run -d --name armada -v ~/.kube/config:/root/.kube/config -v $(pwd)/examples/:/examples -v $(pwd)/etc:/root/armada/etc armada:local

.. note::

    The first build will take a little while. Afterwords, it will build much
    faster.


Virtualenv
##########

We will show you how to set up armada in your local using virtualenv

.. note::

    Suggest that you use a Ubuntu 16.04 VM

1. git clone http://github.com/att-comdev/armada.git && cd armada
2. virtualenv venv
2. source ./venv/bin/activate
3. sudo sh ./tools/libgit2.sh
4. pip install pygit2==0.25.0

Test that it worked with:

.. code-block:: bash

    # We want to validate that libgit2/pygit2 is installed properly
    python -c 'import pygit2'

From the directory of the forked repository:

.. code-block:: bash

    pip install -r requirements.txt
    pip install -r test-requirements.txt
    pip install -e .

    # policy and config are used in order to use and configure Armada API
    tox -e genconfig
    tox -e genpolicy

    armada -h

.. note::

    this will install the latest libgit2 library so you have to make sure you
    install the same version library with pip ( current version: 0.25.0 )

Kubernetes
##########

To test your armada fixes/features you will need to set-up a Kubernetes cluster.

We recommend:

`Kubeadm <https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/>`_

`Kubeadm-AIO <https://github.com/openstack/openstack-helm/tree/master/tools/kubeadm-aio>`_
