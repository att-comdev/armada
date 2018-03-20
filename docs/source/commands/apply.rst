Armada - Apply
==============


Commands
--------

.. code:: bash

    Usage: armada apply [OPTIONS] FILENAME

      This command installs and updates charts defined in armada manifest

      The apply argument must be relative path to Armada Manifest. Executing
      apply command once will install all charts defined in manifest. Re-
      executing apply command will execute upgrade.

      To see how to create an Armada manifest:
      http://armada-helm.readthedocs.io/en/latest/operations/

      To install or upgrade charts, run:

          $ armada apply examples/simple.yaml

      To override a specific value in a Manifest, run:

          $ armada apply examples/simple.yaml --set manifest:simple-armada:release_name="wordpress"

      Or to override several values in a Manifest, reference a values.yaml-
      formatted file:

          $ armada apply examples/simple.yaml --values examples/simple-ovr-values.yaml

    Options:
      --api                         Contacts service endpoint.
      --disable-update-post         Disable post-update Tiller operations.
      --disable-update-pre          Disable pre-update Tiller operations.
      --dry-run                     Run charts without installing them.
      --enable-chart-cleanup        Clean up unmanaged charts.
      --set TEXT                    Use to override Armada Manifest values.
                                    Accepts overrides that adhere to the format
                                    <path>:<to>:<property>=<value> to specify a
                                    primitive or
                                    <path>:<to>:<property>=<value1>,...,<valueN>
                                    to specify a list of values.
      --tiller-host TEXT            Tiller host IP.
      --tiller-port INTEGER         Tiller host port.
      -tn, --tiller-namespace TEXT  Tiller namespace.
      --timeout INTEGER             Specifies time to wait for charts to deploy.
      -f, --values TEXT             Use to override multiple Armada Manifest
                                    values by reading overrides from a
                                    values.yaml-type file.
      --wait                        Wait until all charts deployed.
      --target-manifest TEXT        The target manifest to run. Required for
                                    specifying which manifest to run when multiple
                                    are available.
      --debug                       Enable debug logging.
      --help                        Show this message and exit.

Synopsis
--------

The apply command will consume an armada manifest which contains group of charts
that it will deploy into the tiller service in your Kubernetes cluster.
Executing the ``armada apply`` again on existing armada deployment will start
an update of the armada deployed charts.

``armada apply armada-manifest.yaml [--debug]``

If you remove ``armada/Charts/v1`` from the ``armada/ChartGroups/v1`` in the armada
manifest and execute an ``armada apply`` with the  ``--enable-chart-cleanup`` flag.
Armada will remove undefined releases with the armada manifest's
``release_prefix`` keyword.
