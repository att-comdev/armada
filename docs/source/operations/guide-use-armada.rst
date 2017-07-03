Armada - Using Armada
=====================

Prerequisites
-------------

Kubernetes Cluster

Tiller Service `here <http://github.com/kubernetes/helm>`_

Armada.yaml `here <guide-build-armada-yaml.rst>`_

.. note::

    Need to have provided a storage system prior(ceph, nfs)

Usage
-----

1. Pull or Build the Armada Docker Images:

.. code:: bash

    Pull:

    docker pull quay.io/attcomdev/armada:latest

    Build:

    git clone https://github.com/att-comdev/armada
    cd armada/
    docker build . -t quay.io/attcomdev/armada:latest

2. Run Armada docker container

.. note::

    Make sure to mount your kubeconfig into ``/root/.kube/config`` in
    the container

.. note::

    To run you custom Armada.yamls you need to mount them into the container as
    shown below.
    This example is using ``examples/`` directory in armada `repo <https://github.com/att-comdev/armada/tree/master/examples>`_

.. code:: bash

    docker run -d --net host -p 8000:8000 --name armada -v ~/.kube/config:/root/.kube/config -v $(pwd)/examples/:/examples quay.io/attcomdev/armada:latest


3. Check that tiller is Available

.. code:: bash

    docker exec -it armada armada tiller --status


4. If tiller is up then we can start deploying our armada yamls

.. code:: bash

    docker exec -it armada armada apply /examples/openstack-helm.yaml [ --debug-logging ]

5. To upgrade charts just modify the armada yaml or chart code and re-run ``armada
   apply`` above

6. To check deployed releases:

.. code:: bash

   docker exec -it armada armada tiller --releases
