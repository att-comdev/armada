Fleet Plugin
============

The fleet plugin extends all the functionality of Armada to be used as a plugin with Openstack Helm.

Install Plugin
---------------
::

    To install the fleet plugin, all you have to do is copy the plugin directory into ~/.helm/plugins/

.. code-block:: bash

    git clone https://github.com/att-comdev/armada.git ~/.helm/plugins/

Usage
------

**helm fleet <action> [options]**
::

    helm fleet tiller --status
    helm fleet apply ~/.helm/plugins/armada/examples/simple.yaml
