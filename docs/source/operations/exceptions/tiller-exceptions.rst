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
