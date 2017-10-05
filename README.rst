Armada
======

|Docker Repository on Quay| |Build Status| |Doc Status|

Armada is a tool for managing multiple helm charts with dependencies by centralizing
all configurations in a single Armada yaml and providing lifecycle
hooks for all helm releases.

Roadmap
-------

Detailed roadmap can be viewed `here <https://github.com/att-comdev/armada/milestones>`_

Issues can be reported `on GitHub <https://github.com/att-comdev/armada/issues>`_

Installation
------------

.. code-block:: bash

    docker run -d --net host -p 8000:8000 --name armada -v ~/.kube/config:/armada/.kube/config -v $(pwd)/examples/:/examples quay.io/attcomdev/armada:latest

Using armada `docs <docs/source/operations/guide-use-armada.rst>`_

Getting Started
---------------

Get started guide can be found in our `Getting Started docs <docs/source/development/getting-started.rst>`_

Usage
-----

Before using armada we need to check a few things:

1. you have a properly configure ``~/.kube/config``

   -  ``kubectl config view``
   -  If it does not exist, you can create it using `kubectl`_

2. Check that you have a running Tiller

   -  ``kubectl get pods -n kube-system``

To run armada, simply supply it with your YAML based intention for any
number of charts:

::

    $ armada apply examples/openstack-helm.yaml [--debug-loggging ]

Your output will look something like this:

::

    $ armada apply examples/openstack-helm.yaml 2017-02-10 09:42:36,753
      armada INFO Cloning git:

.. _kubectl: https://kubernetes.io/docs/user-guide/kubectl/kubectl_config/

.. |Docker Repository on Quay| image:: https://quay.io/repository/attcomdev/armada/status
   :target: https://quay.io/repository/attcomdev/armada
.. |Build Status| image:: https://travis-ci.org/att-comdev/armada.svg?branch=master
   :target: https://travis-ci.org/att-comdev/armada
.. |Doc Status| image:: https://readthedocs.org/projects/armada-helm/badge/?version=latest
   :target: http://armada-helm.readthedocs.io/
