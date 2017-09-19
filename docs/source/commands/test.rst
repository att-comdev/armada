Armada - Test
=============


Commands
--------

.. code:: bash

    Usage: armada test [OPTIONS]

      This command test deployed charts

      The tiller command uses flags to obtain information from tiller services.
      The test command will run the release chart tests either via a the
      manifest or by targetings a relase.

      To obtain armada deployed releases:

          $ armada test --file example/simple.yaml

      To obtain tiller service status/information:

          $ armada tiller --release blog-1

    Options:
      --file TEXT            armada manifest
      --release TEXT         helm release
      --tiller-host TEXT     Tiller Host IP
      --tiller-port INTEGER  Tiller host Port
      --help                 Show this message and exit.


Synopsis
--------

The test command will perform helm test defined on the release. Test command can
test a single release or a manifest.
