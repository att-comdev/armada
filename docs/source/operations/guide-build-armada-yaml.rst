Armada - Making Your First Armada Yaml
======================================

Keywords
--------

+---------------------+--------+----------------------+
| keyword             | type   | action               |
+=====================+========+======================+
| ``armada``          | object | define an            |
|                     |        | armada               |
|                     |        | release              |
+---------------------+--------+----------------------+
| ``release_prefix``  | string | tag appended to the  |
|                     |        | front of all         |
|                     |        | charts               |
|                     |        | released             |
|                     |        | by the               |
|                     |        | yaml in              |
|                     |        | order to             |
|                     |        | manage them          |
|                     |        | throughout their     |
|                     |        | lifecycles           |
+---------------------+--------+----------------------+
| ``charts``          | array  | stores the           |
|                     |        | definitions          |
|                     |        | of all               |
|                     |        | charts               |
+---------------------+--------+----------------------+
| ``chart``           | object | definition           |
|                     |        | of the               |
|                     |        | chart                |
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

Chart Group
^^^^^^^^^^^

+-----------------+----------+------------------------------------------------------------------------+
| keyword         | type     | action                                                                 |
+=================+==========+========================================================================+
| description     | string   | description of chart set                                               |
+-----------------+----------+------------------------------------------------------------------------+
| charts_group    | array    | stores definiton of the charts in a group                              |
+-----------------+----------+------------------------------------------------------------------------+
| sequenced       | bool     | enables sequeced chart deployment in a group                           |
+-----------------+----------+------------------------------------------------------------------------+

Chart
^^^^^

+-----------------+----------+------------------------------------------------------------------------+
| keyword         | type     | action                                                                 |
+=================+==========+========================================================================+
| name            | string   | name for the chart                                                     |
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

.. note::

    You can use references in order to build your charts, this will reduce the size of the chart definition will show example in multichart below

Simple Example
~~~~~~~~~~~~~~

::

    armada:
      release_prefix: "my_armada"
      charts:
        - description: I am a chart group
          sequenced: False
          chart_group:
            - chart: &cockroach
              name: cockroach
              release_name: cockroach
              namespace: db
              timeout: 20
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
        - description: I am group 1
          sequenced: True
          chart_group:
            - chart: &common
              name: common
              release_name: common
              namespace: db
              timeout: 20
              install:
                no_hooks: false
              values:
                Replicas: 1
              source:
                type: git
                location: git://github.com/kubernetes/charts/
                subpath: stable/common
                reference: master
              dependencies: []
            - chart: &cockroach
              name: cockroach
              release_name: cockroach
              namespace: db
              timeout: 20
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
        - description: I am group 2
          sequenced: False
          chart_group:
            - chart: &mariadb
              name: mariadb
              release_name: mariadb
              namespace: db
              timeout: 20
              install:
                no_hooks: false
              values:
                Replicas: 1
              source:
                type: git
                location: git://github.com/kubernetes/charts/
                subpath: stable/mariadb
                reference: master
              dependencies: []

References
~~~~~~~~~~

For working examples please check the examples in our repo
`here <https://github.com/att-comdev/armada/tree/master/examples>`__
