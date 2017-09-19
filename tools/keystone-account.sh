#!/usr/bin/env bash

if [ -x $(which openstack) ]; then
    pip install python-openstackclient
fi

openstack domain create 'ucp'
openstack project create --domain 'ucp' 'service'
openstack user create --domain ucp --project service --project-domain 'ucp' --password armada armada
openstack role add --project-domain ucp --user-domain ucp --user armada --project service admin
