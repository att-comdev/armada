Armada - Apply
==============


Commands
--------

.. code:: bash

    Usage: armada apply FILE


    Options:

    [-h] [--dry-run] [--debug-logging] [--disable-update-pre]
    [--disable-update-post] [--enable-chart-cleanup] [--wait]
    [--timeout TIMEOUT]


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
