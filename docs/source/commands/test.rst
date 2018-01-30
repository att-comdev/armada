Armada - Test
=============


Commands
--------

.. code:: bash

    Usage: armada test [OPTIONS]

      This command test deployed charts

      The tiller command uses flags to obtain information from tiller services.
      The test command will run the release chart tests either via a
      manifest or by targeting a release.

      To obtain armada deployed releases:

          $ armada test --file examples/simple.yaml

      To test release:

          $ armada test --release blog-1

    Options:
      --file TEXT                   armada manifest
      --release TEXT                helm release
      --tiller-host TEXT            Tiller Host IP
      --tiller-port INTEGER         Tiller Host Port
      -tn, --tiller-namespace TEXT  Tiller Namespace
      --target-manifest TEXT        The target manifest to run. Required for
                                    specifying which manifest to run when multiple
                                    are available.
      --help                        Show this message and exit.

Synopsis
--------

The test command will perform helm test defined on the release. Test command can
test a single release or a manifest.
