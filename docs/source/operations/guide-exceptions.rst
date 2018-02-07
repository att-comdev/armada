Api Exceptions
==============

+-------------------------+----------------------------------------------------+
| Exception               | Error Description                                  |
+=========================+====================================================+
| ApiException            | Occurs when there is no appropriate API exception  |
|                         | available.                                         |
|                         |                                                    |
|                         | **Message:**                                       |
|                         | *An unknown API error occurred.*                   |
|                         |                                                    |
|                         | **Troubleshoot:**                                  |
|                         | *Coming Soon*                                      |
+-------------------------+----------------------------------------------------+
| ClientError             | Occurs when an error arises during chart cleanup.  |
|                         |                                                    |
|                         | **Message:**                                       |
|                         | *There was an error listing the helm chart         |
|                         | releases.*                                         |
|                         |                                                    |
|                         | **Troubleshoot:**                                  |
|                         | *Coming Soon*                                      |
+-------------------------+----------------------------------------------------+
| ClientForbiddenError    | Occurs when an error arises during chart cleanup.  |
|                         |                                                    |
|                         | **Message:**                                       |
|                         | *There was an error listing the helm chart         |
|                         | releases.*                                         |
|                         |                                                    |
|                         | **Troubleshoot:**                                  |
|                         | *Coming Soon*                                      |
+-------------------------+----------------------------------------------------+
| ClientUnauthorizedError | Occurs when an error arises during chart cleanup.  |
|                         |                                                    |
|                         | **Message:**                                       |
|                         | *There was an error listing the helm chart         |
|                         | releases.*                                         |
|                         |                                                    |
|                         | **Troubleshoot:**                                  |
|                         | *Coming Soon*                                      |
+-------------------------+----------------------------------------------------+

Armada Exceptions
=================

+------------------------+-----------------------------------------------------+
| Exception              | Error Description                                   |
+========================+=====================================================+
| KnownReleasesException | Occurs when no known releases are found.            |
|                        |                                                     |
|                        | **Message:**                                        |
|                        | *No known releases found*                           |
|                        |                                                     |
|                        | **Troubleshoot:**                                   |
|                        | *Coming Soon*                                       |
+------------------------+-----------------------------------------------------+

Base Exceptions
===============

+------------------------+-----------------------------------------------------+
| Exception              | Error Description                                   |
+========================+=====================================================+
| ActionForbidden        | Action Forbidden                                    |
|                        |                                                     |
|                        | **Message:**                                        |
|                        | *Insufficient privilege to perform action.*         |
|                        |                                                     |
|                        | **Troubleshoot:**                                   |
|                        | *Coming Soon*                                       |
+------------------------+-----------------------------------------------------+

Chartbuilder Exceptions
=======================

+-----------------------------+------------------------------------------------+
| Exception                   | Error Description                              |
+=============================+================================================+
| DepedencyException          | A dependency failed to install.                |
|                             |                                                |
|                             | **Message:**                                   |
|                             | *Failed to resolve dependencies for            |
|                             | <chart name>.*                                 |
|                             |                                                |
|                             | **Troubleshoot:**                              |
|                             | *Coming Soon*                                  |
+-----------------------------+------------------------------------------------+
| HelmChartBuildException     | An error occurred building the chart.          |
|                             |                                                |
|                             | **Message:**                                   |
|                             | *Failed to build Helm chart for <chart name>.* |
|                             |                                                |
|                             | **Troubleshoot:**                              |
|                             | *Coming Soon*                                  |
+-----------------------------+------------------------------------------------+
| IgnoredFilesLoadException   | An error occurred loading the ignored files.   |
|                             |                                                |
|                             | **Message:**                                   |
|                             | *An error occurred while loading the ignored   |
|                             | files in .helmignore*                          |
|                             |                                                |
|                             | **Troubleshoot:**                              |
|                             | *Coming Soon*                                  |
+-----------------------------+------------------------------------------------+
| MetadataLoadException       | An error occurred loading the metadata for a   |
|                             | chart.                                         |
|                             |                                                |
|                             | **Message**                                    |
|                             | *Failed to load metadata from chart yaml file* |
|                             |                                                |
|                             | **Troubleshoot:**                              |
|                             | *Coming Soon*                                  |
+-----------------------------+------------------------------------------------+

Lint Exceptions
===============

+----------------------------------+-------------------------------------------+
| Exception                        | Error Description                         |
+==================================+===========================================+
| InvalidArmadaObjectException     |  Armada object not declared.              |
|                                  |                                           |
|                                  | **Message:**                              |
|                                  | *An Armada object was not declared.*      |
|                                  |                                           |
|                                  | **Troubleshoot:**                         |
|                                  | *Coming Soon*                             |
+----------------------------------+-------------------------------------------+
| InvalidManifestException         | Armada manifest invalid.                  |
|                                  |                                           |
|                                  | **Message:**                              |
|                                  | *Armada manifest invalid.*                |
|                                  |                                           |
|                                  | **Troubleshoot:**                         |
|                                  | *Coming Soon*                             |
+----------------------------------+-------------------------------------------+

Manifest Exceptions
===================
+----------------------------------+-------------------------------------------+
| Exception                        | Error Description                         |
+==================================+===========================================+
| ManifestException                | An exception occurred while attempting to |
|                                  | build an Armada manifest. The exception   |
|                                  | will return with details as to why.       |
|                                  |                                           |
|                                  | **Message:**                              |
|                                  | *An error occured while generating the    |
|                                  | manifest: <details>*                      |
|                                  |                                           |
|                                  | **Troubleshoot:**                         |
|                                  | *Coming Soon*                             |
+----------------------------------+-------------------------------------------+

Override Exceptions
===================

+----------------------------------+-------------------------------------------+
| Exception                        | Error Description                         |
+==================================+===========================================+
| InvalidOverrideFileException     | Occurs when an invalid override file is   |
|                                  | provided.                                 |
|                                  |                                           |
|                                  | **Message:**                              |
|                                  | *<filename> is not a valid override file.*|
|                                  |                                           |
|                                  | **Troubleshoot:**                         |
|                                  | *Coming Soon*                             |
+----------------------------------+-------------------------------------------+
| InvalidOverrideValueException    | Occurs when an invalid value is used with |
|                                  | the set flag.                             |
|                                  |                                           |
|                                  | **Message:**                              |
|                                  | *<override command> is not a valid        |
|                                  | override statement.*                      |
|                                  |                                           |
|                                  | **Troubleshoot:**                         |
|                                  | *Coming Soon*                             |
+----------------------------------+-------------------------------------------+
| UnknownDocumentOverrideException | Occurs when an invalid value is used with |
|                                  | the set flag.                             |
|                                  |                                           |
|                                  | **Message:**                              |
|                                  | *Unable to find <document name> document  |
|                                  | schema: <document type>*                  |
|                                  |                                           |
|                                  | **Troubleshoot:**                         |
|                                  | *Coming Soon*                             |
+----------------------------------+-------------------------------------------+

Source Exceptions
=================

+--------------------------+---------------------------------------------------+
| Exception                | Error Description                                 |
+==========================+===================================================+
| ChartSourceException     | Occurs when an unknown chart source type is       |
|                          | encountered.                                      |
|                          |                                                   |
|                          | **Message:**                                      |
|                          | *Unknown source type "<source type>"" for chart   |
|                          | "<chart name>"*                                   |
|                          |                                                   |
|                          | **Troubleshoot:**                                 |
|                          | *Coming Soon*                                     |
+--------------------------+---------------------------------------------------+
| GitException             | Occurs when an error arises cloning a Git         |
|                          | repository.                                       |
|                          |                                                   |
|                          | **Message:**                                      |
|                          | *Git exception occurred, <location> may not be a  |
|                          | valid git repository.*                            |
|                          |                                                   |
|                          | **Troubleshoot:**                                 |
|                          | *Coming Soon*                                     |
+--------------------------+---------------------------------------------------+
| InvalidPathException     | Occurs when a non-existent path is accessed.      |
|                          |                                                   |
|                          | **Message:**                                      |
|                          | *Unable to access path <path>*                    |
|                          |                                                   |
|                          | **Troubleshoot:**                                 |
|                          | *Coming Soon*                                     |
+--------------------------+---------------------------------------------------+
| TarballDownloadException | Occurs when the tarball cannot be downloaded from |
|                          | the provided URL.                                 |
|                          |                                                   |
|                          | **Message:**                                      |
|                          | *Unable to download from <tarball url>*           |
|                          |                                                   |
|                          | **Troubleshoot:**                                 |
|                          | *Coming Soon*                                     |
+--------------------------+---------------------------------------------------+
| TarballExtractException  | Occurs when extracting a tarball fails.           |
|                          |                                                   |
|                          | **Message:**                                      |
|                          | *Unable to extract <tarball directory>*           |
|                          |                                                   |
|                          | **Troubleshoot:**                                 |
|                          | *Coming Soon*                                     |
+--------------------------+---------------------------------------------------+

Tiller Exceptions
=================

+------------------------------------+-----------------------------------------+
| Exception                          | Error Description                       |
+====================================+=========================================+
| ChannelException                   | Occurs during a failed GRPC channel     |
|                                    | creation.                               |
|                                    |                                         |
|                                    | **Message:**                            |
|                                    | *Failed to create GRPC channel*         |
|                                    |                                         |
|                                    | **Troubleshoot:**                       |
|                                    | *Coming Soon*                           |
+------------------------------------+-----------------------------------------+
| GetReleaseStatusException          | Occurs during a failed release testing. |
|                                    |                                         |
|                                    | **Message:**                            |
|                                    | *Failed to get <release> status         |
|                                    | <version>*                              |
|                                    |                                         |
|                                    | **Troubleshoot:**                       |
|                                    | *Coming Soon*                           |
+------------------------------------+-----------------------------------------+
| PostUpdateJobCreateException       | An error occurred creating a job after  |
|                                    | an update.                              |
|                                    |                                         |
|                                    | **Message:**                            |
|                                    | *Failed to create k8s job <name> in     |
|                                    | <namespace>*                            |
|                                    |                                         |
|                                    | **Troubleshoot:**                       |
|                                    | *Coming Soon*                           |
+------------------------------------+-----------------------------------------+
| PreUpdateJobDeleteException        | An error occurred deleting a job before |
|                                    | an update.                              |
|                                    |                                         |
|                                    | **Message:**                            |
|                                    | *Failed to delete k8s job <name> in     |
|                                    | <namespace>*                            |
|                                    |                                         |
|                                    | **Troubleshoot:**                       |
|                                    | *Coming Soon*                           |
+------------------------------------+-----------------------------------------+
| ReleaseException                   | A release failed to complete action.    |
|                                    |                                         |
|                                    | **Message:**                            |
|                                    | *Failed to <action> release: <name> -   |
|                                    | Tiller Message: <tiller message>*       |
|                                    |                                         |
|                                    | **Possible Actions:**                   |
|                                    | *delete, install, test, upgrade*        |
|                                    |                                         |
|                                    | **Troubleshoot:**                       |
|                                    | *Coming Soon*                           |
+------------------------------------+-----------------------------------------+
| TillerPodNotFoundException         | Tiller pod could not be found using the |
|                                    | labels specified in the Armada config.  |
|                                    |                                         |
|                                    | **Message:**                            |
|                                    | *Could not find tiller pod with labels  |
|                                    | "<labels>"*                             |
|                                    |                                         |
|                                    | **Troubleshoot:**                       |
|                                    | *Coming Soon*                           |
+------------------------------------+-----------------------------------------+
| TillerPodNotRunningException       | Tiller pod was found but is not in a    |
|                                    | running state.                          |
|                                    |                                         |
|                                    | **Message:**                            |
|                                    | *No tiller pods found in running state* |
|                                    |                                         |
|                                    | **Troubleshoot:**                       |
|                                    | *Coming Soon*                           |
+------------------------------------+-----------------------------------------+
| TillerServicesUnavailableException | Occurs when Tiller services are         |
|                                    | unavailable.                            |
|                                    |                                         |
|                                    | **Message:**                            |
|                                    | *Tiller services unavailable.*          |
|                                    |                                         |
|                                    | **Troubleshoot:**                       |
|                                    | *Coming Soon*                           |
+------------------------------------+-----------------------------------------+
| TillerVersionException             | Occurs during a failed release testing  |
|                                    |                                         |
|                                    | **Message:**                            |
|                                    | *Failed to get Tiller Version*          |
|                                    |                                         |
|                                    | **Troubleshoot:**                       |
|                                    | *Coming Soon*                           |
+------------------------------------+-----------------------------------------+
