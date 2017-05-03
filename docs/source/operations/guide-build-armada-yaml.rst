Armada - Making Your First Armada Yaml
======================================

Keywords
--------

+---------------------+--------+----------------------+
| keyword             | type   | action               |
+=====================+========+======================+
| ``armada``          | object | will                 |
|                     |        | define an            |
|                     |        | armada               |
|                     |        | release              |
+---------------------+--------+----------------------+
| ``release_prefix``  | string | will tag             |
|                     |        | all                  |
|                     |        | charts               |
|                     |        | released             |
|                     |        | by the               |
|                     |        | yaml in              |
|                     |        | order to             |
|                     |        | manage it            |
|                     |        | the                  |
|                     |        | lifecycle            |
|                     |        | of charts            |
+---------------------+--------+----------------------+
| ``charts``          | array  | will                 |
|                     |        | store the            |
|                     |        | definitio            |
|                     |        | ns                   |
|                     |        | of all               |
|                     |        | your                 |
|                     |        | charts               |
+---------------------+--------+----------------------+
| ``chart``           | object | will                 |
|                     |        | define               |
|                     |        | what your            |
|                     |        | chart                |
|                     |        |                      |
+---------------------+--------+----------------------+

Defining a chart
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

Chart Keywords
^^^^^^^^^^^^^^

Chart
^^^^^

+-----------------+----------+------------------------------------------------------------------------+
| keyword         | type     | action                                                                 |
+=================+==========+========================================================================+
| name            | string   | will be the name fo the chart                                          |
+-----------------+----------+------------------------------------------------------------------------+
| release\_name   | string   | will be the name of the release                                        |
+-----------------+----------+------------------------------------------------------------------------+
| namespace       | string   | will place your chart in define namespace                              |
+-----------------+----------+------------------------------------------------------------------------+
| install         | object   | will install the chart into your kubernetes cluster                    |
+-----------------+----------+------------------------------------------------------------------------+
| update          | object   | will updated any chart managed by the armada yaml                      |
+-----------------+----------+------------------------------------------------------------------------+
| values          | object   | will override any default values in the charts                         |
+-----------------+----------+------------------------------------------------------------------------+
| source          | object   | will provide a path to a ``git repo`` or ``local dir`` deploy chart.   |
+-----------------+----------+------------------------------------------------------------------------+
| dependencies    | object   | will reference any chart deps before install                           |
+-----------------+----------+------------------------------------------------------------------------+

Source
^^^^^^

+-------------+----------+---------------------------------------------------------------+
| keyword     | type     | action                                                        |
+=============+==========+===============================================================+
| type        | string   | will be the source to build the charts ``git`` or ``local``   |
+-------------+----------+---------------------------------------------------------------+
| location    | string   | will be the ``url`` or ``path`` to the charts                 |
+-------------+----------+---------------------------------------------------------------+
| subpath     | string   | will specify the path to target chart                         |
+-------------+----------+---------------------------------------------------------------+
| reference   | string   | will be the branch of the repo                                |
+-------------+----------+---------------------------------------------------------------+

.. note::

    You can use references in order to build your charts, this will reduce the size of the chart definition will show example in multichart below

Simple Example
~~~~~~~~~~~~~~

::

    armada:
       release_prefix: "my_armada"
       charts:
           - chart: &cockroach
            name: cockroach
            release_name: cockroach
            namespace: db
            install:
              no_hooks: false
            values:
                Replicas: 1
            source:
              type: git
              location: git://github.com/kubernetes/charts/
              subpath: stable/cockroachdb
              reference: master
            dependencies: []

Multichart Example
~~~~~~~~~~~~~~~~~~

::

    armada:
       release_prefix: "my_armada"
       charts:
           - chart: &common
             name: common
             release_name: null
             namespace: null
             values: {}
             source:
                type: git
                location: git://github.com/kubernetes/charts/
                subpath: common
                reference: master
             dependencies: []

           - chart: &cockroach
            name: cockroach
            release_name: cockroach
            namespace: db
            install:
              no_hooks: false
            values:
                Replicas: 1
            source:
              type: git
              location: git://github.com/kubernetes/charts/
              subpath: stable/cockroachdb
              reference: master
            dependencies:
                - *common

References
~~~~~~~~~~

For working examples please check the examples in our repo
`here <https://github.com/att-comdev/armada/tree/master/examples>`__
