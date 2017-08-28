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

    docker build . -t armada/latest

    docker run -d --name armada -v ~/.kube/config:/armada/.kube/config -v $(pwd)/examples/:/examples armada/latest

.. note::

    The first build will take a little while. Afterwords, it will build much
    faster.

Virtualenv
##########

To use VirtualEnv:

1. virtualenv venv
2. source ./venv/bin/activate

From the directory of the forked repository:

.. code-block:: bash

    pip install -r requirements.txt
    pip install -r test-requirements.txt

    pip install .

    # Testing your armada code
    # The tox command will execute lint, bandit, cover
    tox

    # For targeted test
    tox -e pep8
    tox -e bandit
    tox -e cover

.. note::

    If building from source, Armada requires that git be installed on
    the system.

Kubernetes
##########

To test your armada fixes/features you will need to set-up a Kubernetes cluster.

We recommend:

`Kubeadm <https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/>`_

`Kubeadm-AIO <https://github.com/openstack/openstack-helm/tree/master/tools/kubeadm-aio>`_
