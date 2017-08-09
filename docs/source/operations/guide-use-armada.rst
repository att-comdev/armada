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

Overriding Manifest Values
--------------------------
It is possible to override manifest values from the command line using the --set and --values flags. When using the set flag, the override type should be specified first, with the target values following in this manner:

.. code:: bash

    armada apply --set [ override_type ].[ target_name ]=[ value ] 

.. note:: 

    When overriding values using the set flag, new values will be inserted if they do not exist. An error will only occur if the correct pattern is not used.

There are three types of override types that can be specified:
- chart
- chart_soure
- release_prefix

An example of overriding the location of a chart:

.. code:: bash

    armada apply --set chart.[ chart_name ].source.location=test [ path_to_manifest ]

An example of overriding the description of a chart group:

.. code:: bash

    armada apply --set chart_group.[ chart_group_name ].description=test [ path_to_manifest]

An example of overriding the release prefix of a manifest:

.. code:: bash

    armada apply --set release_prefix=[ value ] [ path_to_manifest ]

.. note::

    The --set flag can be used multiple times.

It is also possible to override manifest values using values specified in a yaml file using the --values flag. When using the --values flag, a path to the yaml file should be specified in this format:

.. code:: bash

    armada apply --values [ path_to_yaml ] [ path_to_manifest ]

.. note::

    The --values flag, like the --set flag, can be specified more than once. The --set and --values flag can also be specified at the same time; however, overrides specified by the --set flag take precedence over those specified by the --values flag.
   

When creating a yaml file of override values, the override type should be specified first, with the target values following. An example:

.. code:: yaml

    chart_group:
        [ name_of_chart_group ]:
            [ target_to_override ]:  [ value ]
    chart:
        [ name_of_chart ]:
            [ target_to_override ]: [ value ]
    release_prefix: [ value ]
