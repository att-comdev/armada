..
  Copyright 2018 AT&T Intellectual Property.
  All Rights Reserved.

  Licensed under the Apache License, Version 2.0 (the "License"); you may
  not use this file except in compliance with the License. You may obtain
  a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
  License for the specific language governing permissions and limitations
  under the License.

.. _validation:

===================
Document Validation
===================

Validations
===========

Armada, like other UCP components, uses ``jsonschema`` to validate documents
passed to it. This includes dedicated schemas for ``Chart``, ``ChartGroup``
and ``Manifest``.

Validation Schemas
==================

Below are the schemas Armada uses to validate documents.

Armada Schemas
--------------

* Chart schema.

  Chart schema against which all Armada ``Chart`` documents are validated.

  .. literalinclude:: ../../../armada/schemas/armada-chart-schema.yaml
    :language: yaml
    :lines: 15-
    :caption: Armada Chart schema.

  This schema is used to sanity-check all ``Chart`` documents.

* ChartGroup schema.

  ChartGroup schema against which all Armada ``ChartGroup`` documents are
  validated.

  .. literalinclude:: ../../../armada/schemas/armada-chartgroup-schema.yaml
    :language: yaml
    :lines: 15-
    :caption: Armada ChartGroup schema.

  This schema is used to sanity-check all ``ChartGroup`` documents.

* Manifest schema.

  Manifest schema against which all Armada ``Manifest`` documents are
  validated.

  .. literalinclude:: ../../../armada/schemas/armada-manifest-schema.yaml
    :language: yaml
    :lines: 15-
    :caption: Armada Manifest schema.

  This schema is used to sanity-check all ``Manifest`` documents.
