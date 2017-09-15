Armada Plugin
============

The armada plugin extends all the functionality of Armada to be used as a plugin with Helm.

Install Plugin
---------------
::

    To install the Armada plugin, all you have to do is copy the plugin directory into ~/.helm/plugins/

.. code-block:: bash

    git clone https://github.com/att-comdev/armada.git ~/.helm/plugins/

Usage
------

**helm <Name> <action> [options]**
::

    helm armada tiller --status
    helm armada apply ~/.helm/plugins/armada/examples/simple.yaml
