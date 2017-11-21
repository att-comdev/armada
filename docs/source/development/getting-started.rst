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

    git clone http://github.com/att-comdev/armada.git && cd armada

    pip install tox

    tox -e genconfig
    tox -e genpolicy

    docker build . -t armada/latest

    make images


.. code-block:: bash

    # Run Docker Image
    docker run -d --name armada -v ~/.kube/:/armada/.kube/ -v $(pwd)/etc:/etc armada:local


.. note::

    The first build will take a little while. Afterwords, it will build much
    faster.

Virtualenv
##########

How to set up armada in your local using virtualenv:

.. note::

    Suggest that you use a Ubuntu 16.04 VM

From the directory of the forked repository:

.. code-block:: bash


    git clone http://github.com/att-comdev/armada.git && cd armada

    virtualenv -p python3 venv

.. code-block:: bash

    pip install -r requirements.txt -r test-requirements.txt

    make bootstrap      # install only requirements lib
    make bootstrap-all  # install all requirements and tests lib


.. code-block:: bash

    pip install .
    make build


.. code-block:: bash
    # Testing your armada code
    # The tox command will execute lint, bandit, cover

    pip install tox

    tox
    make test-all

    # Linting
    tox -e pep8
    make test-pep8
    make lint

    # Bandit
    tox -e bandit
    make test-bandit

    # Coverage
    tox -e coverage
    make test-coverage

    # build charts
    make charts

    # policy and config are used in order to use and configure Armada API
    tox -e genconfig
    tox -e genpolicy


.. note::

    If building from source, Armada requires that git be installed on
    the system.

Kubernetes
##########

To test your armada fixes/features you will need to set-up a Kubernetes cluster.

We recommend:

`Kubeadm <https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/>`_

`Kubeadm-AIO <https://github.com/openstack/openstack-helm/blob/master/doc/
source/install/developer/all-in-one.rst>`_
