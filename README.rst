Armada
======

|Docker Repository on Quay| |Build Status| |Doc Status|

Armada is a tool for managing multiple Helm charts with dependencies by centralizing
all configurations in a single Armada YAML and providing lifecycle
hooks for all Helm releases.

Armada consists of two separate but complementary components:

#. CLI component (**mandatory**) which interfaces directly with `Tiller`_.
#. API component (**optional**) which services user requests through a wsgi
   server (which in turn communicates with the `Tiller`_ server) and provides
   the following additional functionality:

   * Role-Based Access Control.
   * Limiting projects to specific `Tiller`_ functionality by leveraging
     project-scoping provided by `Keystone`_.

Roadmap
-------

Detailed roadmap can be viewed `here <https://github.com/att-comdev/armada/milestones>`_.

Issues can be reported `on GitHub <https://github.com/att-comdev/armada/issues>`_.

Installation
------------

Quick Start (via Container)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Armada can be most easily installed as a container, which requires Docker to be
executed. To install Docker, please reference the following
`install guide <https://docs.docker.com/engine/installation/>`_.

Afterward, you can launch the Armada container by executing:

.. code-block:: bash

    $ sudo docker run -d --net host -p 8000:8000 --name armada \
      -v ~/.kube/config:/armada/.kube/config \
      -v $(pwd)/examples/:/examples quay.io/attcomdev/armada:latest

Manual Installation
^^^^^^^^^^^^^^^^^^^

Pre-requisites
~~~~~~~~~~~~~~

#. Install and configure `kubectl`_

#. Ensure that ``~/.kube/config`` exists and is properly configured by
   executing::

     $ kubectl config view

   If the file does not exist, please create it by running::

     $ kubectl

#. Install and configure `Tiller`_

#. Verify that Tiller is installed and running correctly by running:

::

  $ kubectl get pods -n kube-system

Installation
~~~~~~~~~~~~

Clone the Armada repository, ``cd`` into it, and execute the following::

  $ sudo apt-get install -y python3-pip
  $ sudo -H pip3 install --upgrade pip
  $ sudo -H pip3 install .

To run Armada, simply supply it with your YAML-based intention for any
number of charts::

  $ armada apply examples/openstack-helm.yaml [--debug-loggging ]

Which should output something like this::

  $ armada apply examples/openstack-helm.yaml 2017-02-10 09:42:36,753

    armada INFO Cloning git:
    ...

For more information on how to install and use Armada, please reference:
:ref:`guide-use-armada`.


Intgration Points
-----------------

Armada CLI component has the following integration points:

  * `Tiller`_ manages Armada chart installations.
  * `Deckhand`_ supplies storage and mangement of site designs and secrets.

In addition, Armada's API component has the following integration points:

  * `Keystone`_ (OpenStack's identity service) provides authentication and
    support for role-based authorization.

Further Reading
---------------

`Undercloud Platform (UCP) <https://github.com/att-comdev/ucp-integration>`_.

.. _kubectl: https://kubernetes.io/docs/user-guide/kubectl/kubectl_config/
.. _Tiller: https://docs.helm.sh/using_helm/#easy-in-cluster-installation
.. _Deckhand: https://github.com/openstack/deckhand
.. _Keystone: https://github.com/openstack/keystone
.. _Promenade: https://github.com/att-comdev/promenade
.. _Shipyard: https://github.com/att-comdev/shipyard

.. |Docker Repository on Quay| image:: https://quay.io/repository/attcomdev/armada/status
   :target: https://quay.io/repository/attcomdev/armada
.. |Build Status| image:: https://travis-ci.org/att-comdev/armada.svg?branch=master
   :target: https://travis-ci.org/att-comdev/armada
.. |Doc Status| image:: https://readthedocs.org/projects/armada-helm/badge/?version=latest
   :target: http://armada-helm.readthedocs.io/
