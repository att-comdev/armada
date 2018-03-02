.. _dev-getting-started:

Developer Install Guide
=======================

Quick Start (via Container)
---------------------------

.. note::

  If actively developing new Armada functionality, it is recommended to proceed
  with :ref:`manual-installation` instead.

To use the docker container to develop:

#. Clone the `Armada repository <http://github.com/att-comdev/armada>`_.
#. ``cd`` into the cloned directory.

   .. code-block:: bash

     $ git clone http://github.com/att-comdev/armada.git && cd armada

#. Next, run the following commands to install ``tox``, generate sample policy
   and configuration files, and build Armada charts as well as the Armada
   container image::

     $ pip install tox

     $ tox -e genconfig
     $ tox -e genpolicy

     $ docker build . -t armada/latest

     $ make images

#. Run the container via Docker::

   $ docker run -d --name armada -v ~/.kube/:/armada/.kube/ -v $(pwd)/etc:/etc armada:local

   .. note::

      The first build will take several minutes. Afterward, it will build much
      faster.

.. _manual-installation:

Manual Installation
-------------------

Pre-requisites
^^^^^^^^^^^^^^

Armada has many pre-requisites because it relies on `Helm`_, which itself
has pre-requisites. The guide below consolidates the installation of all
pre-requisites. For help troubleshooting individual resources, reference
their installation guides.

Armada requires a Kubernetes cluster to be deployed, along with `kubectl`_,
`Helm`_ client, and `Tiller`_ (the Helm server).

#. Install Kubernetes (k8s) and deploy a k8s cluster.

   This can be accomplished by cloning the
   `k8s repo <https://github.com/kubernetes/kubernetes>_` and running
   ``kube-up.sh`` in ``kubernetes/cluster``.

   Alternatively, reference the :ref:`k8s-cluster-management` section below.

#. Install and configure `kubectl`_

#. Ensure that ``~/.kube/config`` exists and is properly configured by
   executing::

     $ kubectl config view

   If the file does not exist, please create it by running::

     $ kubectl

#. Install and configure the `Helm`_ client.

#. Install and configure `Tiller`_ (Helm server).

#. Verify that Tiller is installed and running correctly by running:

::

  $ kubectl get pods -n kube-system

.. _k8s-cluster-management:

Kubernetes Cluster Management
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To test Armada fixes/features a Kubernetes cluster must be installed.

Either software is recommended:

* `Kubeadm <https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/>`_

* `Kubeadm-AIO <https://docs.openstack.org/openstack-helm/latest/install/
  developer/all-in-one.html>`_

.. _armada-cli-installation:

Armada CLI Installation
^^^^^^^^^^^^^^^^^^^^^^^

Follow the steps below to install the Armada CLI.

.. note::

  Some commands below use ``apt-get`` as the package management software.
  Use whichever command corresponds to the Linux distro being used.

.. warning::

  Armada is only tested against a Ubuntu 16.04 environment.

Clone the Armada repository, ``cd`` into it::

  git clone http://github.com/att-comdev/armada.git && cd armada

It is recommended that Armada be run inside a virtual environment. To do so::

  $ virtualenv -p python3 venv
  ...
  >> New python executable in <...>/venv/bin/python3

Afterward, ``source`` the executable::

  source <...>/venv/bin/activate

Next, ensure that ``pip`` is installed.

  $ apt-get install -y python3-pip
  $ pip3 install --upgrade pip

Finally, run (from inside the Armada root directory)::

  $ (venv) make build

The above command will install ``pip`` requirements and execute
``python setup.py build`` within the virtual environment.

Verify that the Armada CLI is installed::

  $ armada --help

Which should emit::

  >> Usage: armada [OPTIONS] COMMAND [ARGS]...
  >>
  >>  Multi Helm Chart Deployment Manager
  ...

Armada API Server Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Armada API server is not required in order to use the Armada CLI,
which in this sense is standalone. The Armada CLI communicates with the Tiller
server and, as such, no API server needs to be instantiated in order for
Armada to communicate with Tiller. The Armada API server and CLI interface
have the exact same functionality. However, the Armada API server offers the
following additional functionality:

  * Role-Based Access Control, allowing Armada to provide authorization around
    specific Armada (and by extension) Tiller functionality.
  * `Keystone`_ authentication and project scoping, providing an additional
     layer of security.

Before proceeding, ensure that the steps in :ref:`armada-cli-installation`
have been followed.

#. Determine where the Armada configuration/deployment files should be stored.
   The default location is ``/etc/armada``. To override the default, run::

     $ export OS_ARMADA_CONFIG_DIR=<desired_path>

#. If the directory specified by ``OS_ARMADA_CONFIG_DIR`` is empty, run
   (from the Armada root directory)::

   $ cp etc/armada/* <OS_ARMADA_CONFIG_DIR>/
   $ mv <OS_ARMADA_CONFIG_DIR>/armada.conf.sample <OS_ARMADA_CONFIG_DIR>/armada.conf

# Install ``uwsgi``::

  $ apt-get install uwsgi -y

#. Ensure that port 8000 is available or else change the ``PORT`` value in
   ``entrypoint.sh``.

#. From the root Armada directory, execute::

   $ ./entrypoint.sh server

#. Verify that the Armada server is running by executing::

   $ TOKEN=$(openstack token issue --format value -c id)
   $ curl -i -X GET localhost:8000/versions -H "X-Auth-Token: $TOKEN"

   Note that the port above uses the default value in ``entrypoint.sh``.

Development Utilities
---------------------

Armada comes equipped with many utilities useful for developers, such as
unit test or linting jobs.

Many of these commands require that ``tox`` be installed. To do so, run::

  $ pip3 install tox

To run the Python linter, execute::

  $ tox -e pep8

  or

  $ make test-pep8

To lint Helm charts, execute::

  $ make lint

To run unit tests, execute::

  $ tox -e py35

  or

  $ make test-unit

To run the test coverage job::

  $ tox -e coverage

  or

  $ make test-coverage

To run security checks via `Bandit`_ execute::

  $ tox -e bandit

  or

  $ make test-bandit

To build the docker images::

  $ make images

To build all Armada charts, execute::

  $ make charts

To build a helm template for the charts::

  $ make dry-run

To run lint, charts, and image targets all at once::

  $ make all

To render any documentation that has build steps::

  $ make docs

To build armada's image::

  $ make run_armada

To build all images::

  $ make run_images

To generate sample configuration and policy files needed for Armada deployment,
execute (respectively)::

  $ tox -e genconfig
  $ tox -e genpolicy

Troubleshooting
---------------

The error messages are included in bullets below and tips to resolution are
included beneath each bullet.

* "FileNotFoundError: [Errno 2] No such file or directory: '/etc/armada/api-paste.ini'"

  Reason: this means that Armada is trying to instantiate the server but
  failing to do so because it can't find an essential configuration file.

  Solution::

    $ cp etc/armada/armada.conf.sample /etc/armada/armada.conf

  This copies the sample Armada configuration file to the appropriate
  directory.

* For any errors related to ``tox``:

  Ensure that ``tox`` is installed::

    $ sudo apt-get install tox -y

* For any errors related to running ``tox -e py35``:

  Ensure that ``python3-dev`` is installed::

    $ sudo apt-get install python3-dev -y

.. _Bandit: https://github.com/openstack/bandit
.. _kubectl: https://kubernetes.io/docs/user-guide/kubectl/kubectl_config/
.. _Helm: https://docs.helm.sh/using_helm/#installing-helm
.. _Keystone: https://github.com/openstack/keystone
.. _Tiller: https://docs.helm.sh/using_helm/#easy-in-cluster-installation
