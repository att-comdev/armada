Armada - Delete
===============


Commands
--------

.. code:: bash

    Usage: armada delete [-f FILE | --release_name RELEASE_NAME]

    Options:

    [-h, --help]                    Show help message and exit
    [-f, --file FILE]               Armada manifest of charts to delete
    [--release_name RELEASE_NAME]   Name of release to delete
    [--tiller-host TILLER_HOST]     Specify the tiller host
    [--tiller-port TILLER_POST]     Specify the tiller port


Synopsis
--------

The delete command will delete a currently deployed helm chart 
from a file or by release name.
