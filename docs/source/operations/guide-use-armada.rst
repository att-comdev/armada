Armada - Using Armada
=====================

Prerequisites
-------------

Kubernetes Cluster

`Tiller Service <http://github.com/kubernetes/helm>`_

`Armada.yaml <guide-build-armada-yaml.rst>`_

.. note::

    Need to have provided a storage system prior(ceph, nfs)

Usage
-----


.. note::

    The apply command performs two main actions: installing and updating define
    charts in the armada manifest

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

    Make sure to mount your kubeconfig into ``/armada/.kube/config`` in
    the container

.. note::

    To run you custom Armada.yamls you need to mount them into the container as
    shown below.
    This example is using ``examples/`` directory in armada `repo <https://github.com/att-comdev/armada/tree/master/examples>`_

.. code:: bash

    docker run -d --net host -p 8000:8000 --name armada -v ~/.kube/config:/root/.kube/config -v $(pwd)/examples/:/examples quay.io/attcomdev/armada:latest

3. Check that tiller is Available

.. code:: bash

    docker exec armada armada tiller --status

4. If tiller is up then we can start deploying our armada yamls

.. code:: bash

    docker exec armada armada apply /examples/openstack-helm.yaml [ --debug-logging ]

5. Upgrading charts: modify the armada yaml or chart source code and run ``armada
   apply`` above

.. code:: bash

    docker exec armada armada apply /examples/openstack-helm.yaml [ --debug-logging ]

6. To check deployed releases:

.. code:: bash

   docker exec armada armada tiller --releases
