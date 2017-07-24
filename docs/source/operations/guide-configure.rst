==================
Configuring Armada
==================


Armada uses an INI-like standard oslo_config file. A sample
file can be generated via tox

.. code-block:: bash

    $ tox -e genconfig

Customize your configuration based on the information below

Keystone Integration
====================

Armada requires a service account to use for validating API
tokens

.. note::

    If you do not have a keystone already deploy, then armada can deploy a keystone service.

    armada apply keystone-manifest.yaml 

.. code-block:: bash

    $ openstack domain create 'ucp'
    $ openstack project create --domain 'ucp' 'service'
    $ openstack user create --domain ucp --project service --project-domain 'ucp' --password armada armada
    $ openstack role add --project-domain ucp --user-domain ucp --user armada --project service admin

    # OR 

    $ ./tools/keystone-account.sh

The service account must then be included in the drydock.conf::

    [keystone_authtoken]
    auth_uri = http://<keystone_ip>:5000/v3
    auth_version = 3
    delay_auth_decision = true
    auth_type = password
    auth_section = keystone_authtoken_password

    [keystone_authtoken_password]
    auth_url = http://<keystone_ip>:5000
    project_name = service
    project_domain_name = ucp
    user_name = armada 
    user_domain_name = ucp
    password = armada
