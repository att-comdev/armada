Armada RESTful API
===================

Armada Endpoints
-----------------

::

    Endpoint: POST /armada/apply

    :string file The yaml file to apply
    :>json boolean debug Enable debug logging
    :>json boolean disable_update_pre
    :>json boolean disable_update_post
    :>json boolean enable_chart_cleanup
    :>json boolean skip_pre_flight
    :>json object values Override manifest values
    :>json boolean dry_run
    :>json boolean wait
    :>json float timeout


::

    Request:

    {
        "file": "examples/openstack-helm.yaml",
        "options": {
            "debug": true,
            "disable_update_pre": false,
            "disable_update_post": false,
            "enable_chart_cleanup": false,
            "skip_pre_flight": false,
            "dry_run": false,
            "wait": false,
            "timeout": false
        }
    }

::

    Results:

    {
        "message": "success"
    }

Tiller Endpoints
-----------------

::

    Endpoint: GET /tiller/releases

    Description: Retrieves tiller releases.


::

    Results:

    {
        "releases": {
            "armada-memcached": "openstack",
            "armada-etcd": "openstack",
            "armada-keystone": "openstack",
            "armada-rabbitmq": "openstack",
            "armada-horizon": "openstack"
        }
    }


::

    Endpoint: GET /tiller/status

    Retrieves the status of the Tiller server.


::

    Results:

    {
        "message": Tiller Server is Active
    }
