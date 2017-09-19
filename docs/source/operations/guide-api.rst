Armada Restful API v1.0
=======================

Description
~~~~~~~~~

The Armada API provides the services similar to the cli via Restful endpoints


Base URL
~~~~~~

https://armada.localhost/api/v1.0/

DEFAULT
~~~~~

GET ``/releases``
-----------------


Summary
+++++++

Get tiller releases



Request
+++++++


Responses
+++++++++

**200**
^^^^^^^

obtain all running releases


**Example:**

.. code-block:: javascript

    {
        "message": {
            "namespace": [
                "armada-release",
                "armada-release"
            ],
            "default": [
                "armada-release",
                "armada-release"
            ]
        }
    }

**403**
^^^^^^^

Unable to Authorize or Permission


**405**
^^^^^^^

Failed to perform action

GET ``/status``
---------------


Summary
+++++++

Get armada running state



Request
+++++++


Responses
+++++++++

**200**
^^^^^^^

obtain armada status

**Example:**

.. code-block:: javascript

    {
        "message": {
            "tiller": {
                "state": True,
                "version": "v2.5.0"
            }
        }
    }

**403**
^^^^^^^

Unable to Authorize or Permission


**405**
^^^^^^^

Failed to perform action


GET ``/validate``
-----------------


Summary
+++++++

Get tiller releases


Request
+++++++


Responses
+++++++++

**200**
^^^^^^^

obtain all running releases


**Example:**

.. code-block:: javascript

    {
        "valid": true
    }

**403**
^^^^^^^

Unable to Authorize or Permission


**405**
^^^^^^^

Failed to perform action


POST ``/apply``
---------------


Summary
+++++++

Install/Update Armada Manifest

Request
+++++++

Body
^^^^

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        disable-update-post | Yes |  |  |  |
        disable-update-pre | Yes |  |  |  |
        dry-run | Yes |  |  |  |
        enable-chart-cleanup | Yes |  |  |  |
        tiller-host | string |  |  |  |
        tiller-port | int |  |  |  |
        timeout | int |  |  |  |
        wait | boolean |  |  |  |


**Armada schema:**

.. code-block:: javascript

    {
        "api": true,
        "armada": {}
    }

Responses
+++++++++

**200**
^^^^^^^

Succesfull installation/update of manifest

**Example:**

.. code-block:: javascript

    {
        "message": {
            "installed": [
                "armada-release",
                "armada-release"
            ],
            "updated": [
                "armada-release",
                "armada-release"
            ],
            "diff": [
                "values": "value diff",
                "values": "value diff 2"
            ]
        }
    }

**403**
^^^^^^^

Unable to Authorize or Permission


**405**
^^^^^^^

Failed to perform action


POST ``/test/{release}``
------------------------


Summary
+++++++

Test release name


Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        release | path | Yes | string |  |  | name of the release to test


Request
+++++++


Responses
+++++++++

**200**
^^^^^^^

Succesfully Test release response

**Example:**

.. code-block:: javascript

    {
        "message": {
            "message": "armada-release",
            "result": "No test found."
        }
    }

**403**
^^^^^^^

Unable to Authorize or Permission


**405**
^^^^^^^

Failed to perform action

POST ``/tests``
---------------


Summary
+++++++

Test manifest releases

Request
+++++++

Body
^^^^

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        armada | Yes |  |  |  |

**Armada schema:**

.. code-block:: javascript

    {
        "armada": {}
    }

Responses
+++++++++

**200**
^^^^^^^

Succesfully Test of manifest

**Example:**

.. code-block:: javascript

    {
        "message": {
            "failed": [
                "armada-release",
                "armada-release"
            ],
            "passed": [
                "armada-release",
                "armada-release"
            ],
            "skipped": [
                "armada-release",
                "armada-release"
            ]
        }
    }

**403**
^^^^^^^

Unable to Authorize or Permission


**405**
^^^^^^^

Failed to perform action

Data Structures
~~~~~~~~~~~~~

Armada Request Model Structure
------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        disable-update-post | Yes |  |  |  |
        disable-update-pre | Yes |  |  |  |
        dry-run | Yes |  |  |  |
        enable-chart-cleanup | Yes |  |  |  |
        tiller-host | string |  |  |  |
        tiller-port | int |  |  |  |
        timeout | int |  |  |  |
        wait | boolean |  |  |  |

**Armada schema:**

Armada Response Model Structure
-------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        message | No |  |  |  |

**Message schema:**

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        installed | No | array of string |  |  |
        updated | No | array of string |  |  |
        values | No | array of string |  |  |


Releases Response Model Structure
---------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        message | No |  |  |  |

**Message schema:**


.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        namespace | No | array of string |  |  |

Status Response Model Structure
-------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        message | No |  |  |  |



**Message schema:**


.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        tiller | No |  |  |  |



**Tiller schema:**


.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        state | No | string |  |  |
        version | No | string |  |  |



Test Response Model Structure
-----------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        message | No |  |  |  |

**Message schema:**


.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        message | No | string |  |  |
        result | No | string |  |  |

Tests Request Model Structure
-----------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        armada | Yes |  |  |  |



**Armada schema:**


Tests Response Model Structure
------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        message | No |  |  |  |


**Message schema:**


.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        failed | No | array of string |  |  |
        passed | No | array of string |  |  |
        skipped | No | array of string |  |  |


Validate Response Model Structure
---------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        valid | No | boolean |  |  |
