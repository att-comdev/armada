Armada - Tiller
===============


Commands
--------

.. code:: bash

    Usage: armada tiller [OPTIONS]

      This command gets tiller information

      The tiller command uses flags to obtain information from tiller services

      To obtain armada deployed releases:

          $ armada tiller --releases

      To obtain tiller service status/information:

          $ armada tiller --status

    Options:
      --tiller-host TEXT     Tiller host ip
      --tiller-port INTEGER  Tiller host port
      --releases             list of deployed releses
      --status               Status of Armada services
      --help                 Show this message and exit.

Synopsis
--------

The tiller command will perform command directly with tiller to check if tiller
in the cluster is running and the list of releases in tiller cluster.
