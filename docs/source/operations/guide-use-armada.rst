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

    docker run -d --net host -p 8000:8000 --name armada -v ~/.kube/config:/armada/.kube/config -v $(pwd)/examples/:/examples quay.io/attcomdev/armada:latest

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

Overriding Manifest Values
--------------------------
It is possible to override manifest values from the command line using the
--set and --values flags. When using the set flag, the document type should be
specified first, with the target values following in this manner:

.. code:: bash

    armada apply --set [ document_type ]:[ document_name ]:[ data_value ]=[ value ]

.. note::

    When overriding values using the set flag, new values will be inserted if
    they do not exist. An error will only occur if the correct pattern is
    not used.

There are three types of override types that can be specified:
- chart
- chart_soure
- release_prefix

An example of overriding the location of a chart:

.. code:: bash

    armada apply --set chart:[ chart_name ]:source.location=test [ FILE ]

    Example:

    armada apply --set chart:blog-1:release=test [ FILE ]

An example of overriding the description of a chart group:

.. code:: bash

    armada apply --set chart_group:[ chart_group_name ]:description=test [ FILE ]

    Example:

    armada apply examples/simple.yaml --set chart_group:blog-group:description=test

An example of overriding the release prefix of a manifest:

.. code:: bash

    armada apply --set manifest:[ manifest_name ]:release_prefix=[ value ] [ FILE ]

    Example:

    armada apply example/simple.yaml --set manifest:simple-armada:release_prefix=armada-2

.. note::

    The --set flag can be used multiple times.

It is also possible to override manifest values using values specified in a
yaml file using the --values flag. When using the --values flag, a path to the
yaml file should be specified in this format:

.. code:: bash

    armada apply --values [ path_to_yaml ] [ FILE ]

    Example:

    armada apply examples/simple.yaml --values examples/simple-ovr-values.yaml

.. note::

    The --values flag, like the --set flag, can be specified more than once.
    The --set and --values flag can also be specified at the same time;
    however, overrides specified by the --set flag take precedence over those
    specified by the --values flag.


When creating a yaml file of override values, it should be the same as creating
an armada manifest overriding documents with the same schema and metadata name
for example:

.. code:: yaml

    ---
    schema: armada/Chart/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-1
    data:
      release: chart-example
      namespace: blog-blog
    ---
    schema: armada/Chart/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-2
    data:
      release: chart-example-2
      namespace: blog-blog
    ---
    schema: armada/ChartGroup/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-group
    data:
      description: Change value deploy
      chart_group:
        - blog-1
