Armada - Making Your First Armada Manifest
==========================================

armada/Manifest/v1
------------------

+---------------------+--------+----------------------+
| keyword             | type   | action               |
+=====================+========+======================+
| ``release_prefix``  | string | appends to the       |
|                     |        | front of all         |
|                     |        | charts               |
|                     |        | released             |
|                     |        | by the               |
|                     |        | manifest in          |
|                     |        | order to             |
|                     |        | manage releases      |
|                     |        | throughout their     |
|                     |        | lifecycle            |
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
| test_charts     | bool     | run pre-defined helm tests helm in a ChartGroup                        |
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

+-----------------+----------+---------------------------------------------------------------------------+
| keyword         | type     | action                                                                    |
+=================+==========+===========================================================================+
| chart\_name     | string   | name for the chart                                                        |
+-----------------+----------+---------------------------------------------------------------------------+
| release\_name   | string   | name of the release                                                       |
+-----------------+----------+---------------------------------------------------------------------------+
| namespace       | string   | namespace of your chart                                                   |
+-----------------+----------+---------------------------------------------------------------------------+
| timeout         | int      | time (in seconds) allotted for chart to deploy when 'wait' flag is set    |
+-----------------+----------+---------------------------------------------------------------------------+
| test            | bool     | run pre-defined helm tests helm in a chart                                |
+-----------------+----------+---------------------------------------------------------------------------+
| install         | object   | install the chart into your Kubernetes cluster                            |
+-----------------+----------+---------------------------------------------------------------------------+
| update          | object   | update the chart managed by the armada yaml                               |
+-----------------+----------+---------------------------------------------------------------------------+
| values          | object   | override any default values in the charts                                 |
+-----------------+----------+---------------------------------------------------------------------------+
| source          | object   | provide a path to a ``git repo``, ``local dir``, or ``tarball url`` chart |
+-----------------+----------+---------------------------------------------------------------------------+
| dependencies    | object   | reference any chart dependencies before install                           |
+-----------------+----------+---------------------------------------------------------------------------+

Update - Pre or Post
^^^^^^^^^^^^^^^^^^^^

+-------------+----------+---------------------------------------------------------------+
| keyword     | type     | action                                                        |
+=============+==========+===============================================================+
| pre         | object   | actions prior to updating chart                               |
+-------------+----------+---------------------------------------------------------------+
| post        | object   | actions post updating chart                                   |
+-------------+----------+---------------------------------------------------------------+


Update - Actions
^^^^^^^^^^^^^^^^

+-------------+----------+---------------------------------------------------------------+
| keyword     | type     | action                                                        |
+=============+==========+===============================================================+
| update      | object   | updates daemonsets in pre update actions                      |
+-------------+----------+---------------------------------------------------------------+
| delete      | object   | delete jobs in pre delete actions                             |
+-------------+----------+---------------------------------------------------------------+


.. note::

    Update actions are performed in the pre/post sections of update


Update - Actions - Update/Delete
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+-------------+----------+---------------------------------------------------------------+
| keyword     | type     | action                                                        |
+=============+==========+===============================================================+
| name        | string   | name of action                                                |
+-------------+----------+---------------------------------------------------------------+
| type        | string   | type of kubernetes workload  to execute                       |
+-------------+----------+---------------------------------------------------------------+
| labels      | object   | array of labels to query against kinds. (key: value)          |
+-------------+----------+---------------------------------------------------------------+

.. note::

   Update Actions only support type: 'daemonset'

.. note::

   Delete Actions only support type: 'job'

Example
~~~~~~~

::

    # type git
    ---
    schema: armada/Chart/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-1
    data:
      chart_name: blog-1
      release_name: blog-1
      namespace: default
      timeout: 100
      install:
        no_hook: false
      upgrade:
        no_hook: false
      values: {}
      source:
        type: git
        location: https://github.com/namespace/repo
        subpath: .
        reference: master
      dependencies: []

    # type local
    ---
    schema: armada/Chart/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-1
    data:
      chart_name: blog-1
      release_name: blog-1
      namespace: default
      timeout: 100
      install:
        no_hook: false
      upgrade:
        no_hook: false
      values: {}
      source:
        type: local
        location: /path/to/charts
        subpath: chart
        reference: master
      dependencies: []

    # type tar
    ---
    schema: armada/Chart/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-1
    data:
      chart_name: blog-1
      release_name: blog-1
      namespace: default
      timeout: 100
      install:
        no_hook: false
      upgrade:
        no_hook: false
      values: {}
      source:
        type: tar
        location: https://localhost:8879/charts/chart-0.1.0.tgz
        subpath: mariadb
        reference: null
      dependencies: []


Source
^^^^^^

+-------------+----------+-------------------------------------------------------------------------------+
| keyword     | type     | action                                                                        |
+=============+==========+===============================================================================+
| type        | string   | source to build the chart: ``git``, ``local``, or ``tar``                     |
+-------------+----------+-------------------------------------------------------------------------------+
| location    | string   | ``url`` or ``path`` to the chart's parent directory                           |
+-------------+----------+-------------------------------------------------------------------------------+
| subpath     | string   | (optional) relative path to target chart from parent (``.`` if not specified) |
+-------------+----------+-------------------------------------------------------------------------------+
| reference   | string   | (optional) branch of the repo (``master`` if not specified)                   |
+-------------+----------+-------------------------------------------------------------------------------+


Example
~~~~~~~

::

    ---
    schema: armada/Chart/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-1
    data:
      chart_name: blog-1
      release_name: blog-1
      namespace: default
      timeout: 100
      install:
        no_hook: false
      upgrade:
        no_hook: false
        pre:
            update:
                - name: test-daemonset
                  type: daemonset
                  labels:
                    foo: bar
                    component: bar
                    rak1: enababled
            delete:
                - name: test-job
                  type: job
                  labels:
                    foo: bar
                    component: bar
                    rak1: enababled
      values: {}
      source:
        type: git
        location: https://github.com/namespace/repo
        subpath: .
        reference: master
      dependencies: []




Defining a Manifest
~~~~~~~~~~~~~~~~~~~

To define your Manifest you need to define a ``armada/Manifest/v1`` document,
``armada/ChartGroup/v1`` document, ``armada/Chart/v1``.
Following the definitions above for each document you will be able to construct
an armada manifest.

Armada - Deploy Behavior
^^^^^^^^^^^^^^^^^^^^^^^^

1. Armada will perform set of pre-flight checks to before applying the manifest
   - validate input manifest
   - check tiller service is Running
   - check chart source locations are valid

2. Deploying Armada Manifest

   1. If the chart is not found

      -  we will install the chart


   3. If exist then

      -  Armada will check if there are any differences in the chart
      -  if the charts are different then it will execute an upgrade
      -  else it will not perform any actions

.. note::

    You can use references in order to build your charts, this will reduce
    the size of the chart definition will show example in multichart below

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
        location: http://github.com/namespace/repo
        subpath: blog-1
        reference: new-feat
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
        subpath: blog1
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
        type: tar
        location: https://github.com/namespace/repo/blog2.tgz
        subpath: blog2
      dependencies: []
    ---
    schema: armada/Chart/v1
    metadata:
      schema: metadata/Document/v1
      name: blog-3
    data:
      chart_name: blog-3
      release: blog-3
      namespace: default
      values: {}
      source:
        type: local
        location: /home/user/namespace/repo/blog3
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
        - blog-3
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
