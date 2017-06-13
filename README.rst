Armada
======

|Docker Repository on Quay| |Build Status| |Doc Status|

A python orchestrator for a installing, upgrading, and managing a
collection of helm charts, dependencies, and values overrides.

Note that this project is pre-alpha and under active development. It may
undergo drastic changes to support the long-term vision but
contributions are welcome.

Overview
--------

The armada python library and command line tool provides a way to
synchronize a helm (tiller) target with an operators intended state,
consisting of several charts, dependencies, and overrides using a single
file or directory with a collection of files. This allows operators to
define many charts, potentially with different namespaces for those
releases, and their overrides in a central place. With a single command,
deploy and/or upgrade them where applicable.

Armada also supports fetching helm chart source and then building charts
from source from various local and remote locations, such as git/github
endpoints. In the future, it may supprot other mechanisms as well.

It will also give the operator some indication of what is about to
change by assisting with diffs for both values, values overrides, and
actual template changes.

Its functionality may extend beyond helm, assisting in interacting with
kubernetes directly to perform basic pre and post steps, such as
removing completed or failed jobs, running backup jobs, blocking on
chart readiness, or deleting resources that do not support upgrades.
However, primarily, it will be an interface to support orchestrating
Helm.

Running Armada
--------------

To use this container, use these simple instructions:

::

    docker run -d --name armada -p 8000:8000 -v ~/.kube/config:/root/.kube/config -v $(pwd)/examples/:/examples -v /tmp:/dev/log quay.io/attcomdev/armada:latest

Manual Install
~~~~~~~~~~~~~~

If you want to build the docker image, follow these steps:

::

    docker build . -t <namespace>/armada
    docker run -d --name armada -p 8000:8000 -v ~/.kube/config:/root/.kube/config -v $(pwd)/examples/:/examples <namespace>/armada

Installation
------------

The installation is fairly straight forward:

Recomended Enviroment: Ubuntu 16.04

Installing Dependecies:
~~~~~~~~~~~~~~~~~~~~~~~

you can run:

-  ``tox testenv:ubuntu`` or ``sudo sh tools/libgit2.sh``
-  ``sudo pip install -r requirements.txt``

NOTE: If you want to use virtualenv please refer to `pygit2`_

Installing armada:
~~~~~~~~~~~~~~~~~~

``sudo pip install -e .``

``armada [-h | --help]``

Using Armada
------------

Before using armada we need to check a few things:

1. you have a properly configure ``~/.kube/config``

   -  ``kubectl config view``
   -  If it does not exist, you can create it using `kubectl`_

2. Check that you have a running Tiller

   -  ``kubectl get pods -n kube-system``

To run armada, simply supply it with your YAML based intention for any
number of charts:

::

    $ armada apply examples/openstack-helm.yaml [--debug ]

Your output will look something like this:

::

    $ armada apply examples/openstack-helm.yaml 2017-02-10 09:42:36,753
      armada INFO Cloning git:

.. _pygit2: http://www.pygit2.org/install.html#libgit2-within-a-virtual-environment
.. _kubectl: https://kubernetes.io/docs/user-guide/kubectl/kubectl_config/

.. |Docker Repository on Quay| image:: https://quay.io/repository/attcomdev/armada/status
   :target: https://quay.io/repository/attcomdev/armada
.. |Build Status| image:: https://travis-ci.org/att-comdev/armada.svg?branch=master
   :target: https://travis-ci.org/att-comdev/armada
.. |Doc Status| image:: https://readthedocs.org/projects/armada-helm/badge/?version=latest
   :target: http://armada-helm.readthedocs.io/

