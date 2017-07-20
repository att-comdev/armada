Armada - Making Your First Armada Manifest
==========================================

armada/Manifest/v1
------------------

+---------------------+--------+----------------------+
| keyword             | type   | action               |
+=====================+========+======================+
| ``release_prefix``  | string | tag appended to the  |
|                     |        | front of all         |
|                     |        | charts               |
|                     |        | released             |
|                     |        | by the               |
|                     |        | yaml in              |
|                     |        | order to             |
|                     |        | manage releses       |
|                     |        | throughout their     |
|                     |        | lifecycles           |
+---------------------+--------+----------------------+
| ``chart_groups``    | array  | references           |
|                     |        | ChartGroup document  |
|                     |        | of all groups        |
|                     |        |                      |
+---------------------+--------+----------------------+

Example
~~~~~~~~

::

    ---
    schema: armada/Manifest/v1
    metadata:
        schema: metadata/Document/v1
        name: simple-armada
    data:
        release_prefix: armada
        chart_groups:
            - chart_group


armada/ChartGroup/v1
--------------------

+-----------------+----------+------------------------------------------------------------------------+
| keyword         | type     | action                                                                 |
+=================+==========+========================================================================+
| description     | string   | description of chart set                                               |
+-----------------+----------+------------------------------------------------------------------------+
| chart_group     | array    | reference to chart document                                            |
+-----------------+----------+------------------------------------------------------------------------+
| sequenced       | bool     | enables sequenced chart deployment in a group                          |
+-----------------+----------+------------------------------------------------------------------------+

Example
~~~~~~~~

::

    ---
    schema: armada/ChartGroup/v1
    metadata:
        schema: metadata/Document/v1
        name: blog-group
    data:
        description: Deploys Simple Service
        sequenced: False
        chart_group:
            - chart
            - chart

armada/Chart/v1
---------------

Chart
^^^^^

+-----------------+----------+------------------------------------------------------------------------+
| keyword         | type     | action                                                                 |
+=================+==========+========================================================================+
| chart\_name      | string   | name for the chart                                                     |
+-----------------+----------+------------------------------------------------------------------------+
| release\_name   | string   | name of the release                                                    |
+-----------------+----------+------------------------------------------------------------------------+
| namespace       | string   | namespace of your chart                                                |
+-----------------+----------+------------------------------------------------------------------------+
| timeout         | int      | time (in seconds) allotted for chart to deploy when 'wait' flag is set |
+-----------------+----------+------------------------------------------------------------------------+
| install         | object   | install the chart into your Kubernetes cluster                         |
+-----------------+----------+------------------------------------------------------------------------+
| update          | object   | update the chart managed by the armada yaml                            |
+-----------------+----------+------------------------------------------------------------------------+
| values          | object   | override any default values in the charts                              |
+-----------------+----------+------------------------------------------------------------------------+
| source          | object   | provide a path to a ``git repo`` or ``local dir`` deploy chart.        |
+-----------------+----------+------------------------------------------------------------------------+
| dependencies    | object   | reference any chart dependencies before install                        |
+-----------------+----------+------------------------------------------------------------------------+

Source
^^^^^^

+-------------+----------+---------------------------------------------------------------+
| keyword     | type     | action                                                        |
+=============+==========+===============================================================+
| type        | string   | source to build the chart: ``git`` or ``local``               |
+-------------+----------+---------------------------------------------------------------+
| location    | string   | ``url`` or ``path`` to the chart's parent directory           |
+-------------+----------+---------------------------------------------------------------+
| subpath     | string   | relative path to target chart from parent                     |
+-------------+----------+---------------------------------------------------------------+
| reference   | string   | branch of the repo                                            |
+-------------+----------+---------------------------------------------------------------+

Defining a Chart
~~~~~~~~~~~~~~~~

To define your charts is not any different than helm. we do provide some
post/pre actions that will help us manage our charts better.

Behavior
^^^^^^^^

1. will check if chart exists

   1. if it does not exist

      -  we will install the chart

   2. if exist then

      -  armada will check if there are any differences in the charts
      -  if the charts are different then it will execute an upgrade
      -  else it will not perform any actions

.. note::

    You can use references in order to build your charts, this will reduce the size of the chart definition will show example in multichart below

Simple Example
~~~~~~~~~~~~~~

::

    ---
    schema: armada/Chart/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-1
    data:
      chart_name: blog-1
      release: blog-1
      namespace: default
      values: {}
      source:
        type: git
        location: https://github.com/namespace/repo
        subpath: .
        reference: master
      dependencies: []
    ---
    schema: armada/ChartGroup/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-group
    data:
      description: Deploys Simple Service
      sequenced: False
      chart_group:
        - blog-1
    ---
    schema: armada/Manifest/v1
    metadata:
      schema: metadata/Document/v1
      name: simple-armada
    data:
      release_prefix: armada
      chart_groups:
        - blog-group

Multichart Example
~~~~~~~~~~~~~~~~~~

::

    ---
    schema: armada/Chart/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-1
    data:
      chart_name: blog-1
      release: blog-1
      namespace: default
      values: {}
      source:
        type: git
        location: https://github.com/namespace/repo
        subpath: .
        reference: master
      dependencies: []
    ---
    schema: armada/Chart/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-2
    data:
      chart_name: blog-2
      release: blog-2
      namespace: default
      values: {}
      source:
        type: git
        location: https://github.com/namespace/repo
        subpath: .
        reference: master
      dependencies: []
    ---
    schema: armada/ChartGroup/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-group-1
    data:
      description: Deploys Simple Service
      sequenced: False
      chart_group:
        - blog-2
    ---
    schema: armada/ChartGroup/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-group-2
    data:
      description: Deploys Simple Service
      sequenced: False
      chart_group:
        - blog-1
    ---
    schema: armada/Manifest/v1
    metadata:
      schema: metadata/Document/v1
      name: simple-armada
    data:
      release_prefix: armada
      chart_groups:
        - blog-group-1
        - blog-group-2

References
~~~~~~~~~~

For working examples please check the examples in our repo
`here <https://github.com/att-comdev/armada/tree/master/examples>`__
