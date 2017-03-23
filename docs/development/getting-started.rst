***********
Development
***********

Docker
######

To use this container, use these simple instructions:

.. code-block:: bash

   docker run quay.io/attcomdev/armada:latest

Virtualenv
##########

To use VirtualEnv we will need to add some extra steps

1. virtualenv venv
2. source ./venv/bin/activate
3. export LIBGIT2=$VIRTUAL_ENV
4. run modified bash below


.. code-block:: bash

    #!/bin/sh

    # Ubuntu 16.04 Install only

    sudo apt install git cmake make -y
    sudo apt-get install -y python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libssh2-1 libgit2-dev python-pip libgit2-24
    sudo apt-get install -y pkg-config libssh2-1-dev libhttp-parser-dev libssl-dev libz-dev

    LIBGIT_VERSION='0.25.0'

    wget https://github.com/libgit2/libgit2/archive/v${LIBGIT_VERSION}.tar.gz
    tar xzf v${LIBGIT_VERSION}.tar.gz
    cd libgit2-${LIBGIT_VERSION}/
    cmake . -DCMAKE_INSTALL_PREFIX=$LIBGIT2
    make
    sudo make install
    export LDFLAGS="-Wl,-rpath='$LIBGIT2/lib',--enable-new-dtags $LDFLAGS"
    sudo pip install pygit2==${LIBGIT_VERSION}
    sudo ldconfig

Test that it worked with:

.. code-block:: bash

   python -c 'import pygit2'


.. code-block:: bash

   git clone https://github.com/att-comdev/armada.git
   cd armada
   pip install -r requirements.txt
   pip install -r test-requirements.txt

Your env is now ready to go! :)

.. note:: this will install latest libgit2 library so you have to make sure you install the same version library with pip ( current version: 0.25.0 )

Kubernetes
##########

To test your armada fixes/features you will need to set-up a Kubernetes cluster. We recommend:

`Minikube <https://github.com/kubernetes/minikube#installation>`_

`Halcyon <https://github.com/att-comdev/halcyon-vagrant-kubernetes>`_

.. note:: When using Halcyon it will not generate a config file. Run the following commands to create one: `get_k8s_creds.sh <https://github.com/att-comdev/halcyon-vagrant-kubernetes#accessing-the-cluster>`_
