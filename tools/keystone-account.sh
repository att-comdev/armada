#!/usr/bin/env bash

OPENSTACK_CLI=$(pip freeze | grep 'python-openstackclient')

if [ $OPENSTACK_CLI == '' ]; then
    pip install python-openstackclient
fi

openstack domain create 'ucp'
openstack project create --domain 'ucp' 'service'
openstack user create --domain ucp --project service --project-domain 'ucp' --password armada armada
openstack role add --project-domain ucp --user-domain ucp --user armada --project service admin
