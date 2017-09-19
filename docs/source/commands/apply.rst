Armada - Apply
==============


Commands
--------

.. code:: bash

    Usage: armada apply [OPTIONS] FILENAME

      This command install and updates charts defined in armada manifest

      The apply argument must be relative path to Armada Manifest. Executing
      apply commnad once will install all charts defined in manifest. Re-
      executing apply commnad will execute upgrade.

      To see how to create an Armada manifest:     http://armada-
      helm.readthedocs.io/en/latest/operations/

      To obtain install/upgrade charts:

          $ armada apply example/simple.yaml

      To obtain override manifest:

          $ armada apply example/simple.yaml --set manifest:simple-armada:relase_name="wordpress"

          or

          $ armada apply example/simple.yaml --values examples/simple-ovr-values.yaml

    Options:
      --api                   Contacts service endpoint
      --disable-update-post   run charts without install
      --disable-update-pre    run charts without install
      --dry-run               run charts without install
      --enable-chart-cleanup  Clean up Unmanaged Charts
      --set TEXT
      --tiller-host TEXT      Tiller host ip
      --tiller-port INTEGER   Tiller host port
      --timeout INTEGER       specifies time to wait for charts
      -f, --values TEXT
      --wait                  wait until all charts deployed
      --help                  Show this message and exit.

Synopsis
--------

The apply command will consume an armada manifest which contains group of charts
that it will deploy into the tiller service in your kubernetes cluster.
Executing the ``armada apply`` again on existing armada deployement will start
an update of the armada deployed charts.

``amada apply armada-manifest.yaml [--debug-logging]``

If you remove ``armada/Charts/v1`` from the ``armada/ChartGroups/v1`` in the armada
manifest and exectute an ``armada apply`` with the  ``--enable-chart-cleanup`` flag.
Armada will remove undefiend releases with the armada manifest's
``release_prefix`` keyword.
