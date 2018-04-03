# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import yaml

from armada.tests.unit import base
from armada.utils import validate
from armada.utils.validation.schema_validate import SchemaValidator


manifest1 = """
schema: armada/Manifest/v1
metadata:
    schema: metadata/Document/v1
    name: example-manifest
data:
    release_prefix: example
    chart_groups:
        - example-chart
"""

group1 = """
schema: armada/ChartGroup/v1
metadata:
  schema: metadata/Document/v1
  name: example-group1
data:
  description: "Example group 1"
  sequenced: False
  test_charts: False
  chart_group:
    - example-chart1
"""

chart1 = """
schema: armada/Chart/v1
metadata:
  schema: metadata/Document/v1
  name: example-chart1
data:
  chart_name: example-chart
  release: example
  namespace: example
  source:
    type: git
    location: https://github.com/att-comdev/armada.git
    subpath: .
    reference: master
  dependencies: []
"""


class BaseSchemaValidatorTest(base.ArmadaTestCase):
    def setUp(self):
        super(BaseSchemaValidatorTest, self).setUp()
        self.manifest = yaml.safe_load(manifest1)
        self.group = yaml.safe_load(group1)
        self.chart = yaml.safe_load(chart1)


class SchemaValidatorTestCase(BaseSchemaValidatorTest):

    def test_validate_manifest_passes(self):
        validator = SchemaValidator(validate.SCHEMAS)
        continue_running = validator.validate(self.manifest)

        self.assertTrue(continue_running)
        self.assertEquals(0, validator.error_counter)
        self.assertEquals(0, len(validator.messages))

    def test_validate_group_passes(self):
        validator = SchemaValidator(validate.SCHEMAS)
        continue_running = validator.validate(self.group)

        self.assertTrue(continue_running)
        self.assertEquals(0, validator.error_counter)
        self.assertEquals(0, len(validator.messages))

    def test_validate_chart_passes(self):
        validator = SchemaValidator(validate.SCHEMAS)
        continue_running = validator.validate(self.chart)

        self.assertTrue(continue_running)
        self.assertEquals(0, validator.error_counter)
        self.assertEquals(0, len(validator.messages))

    def test_validate_manifest_without_required_release_prefix(self):
        template_manifest = """
        schema: armada/Manifest/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            chart_groups:
                - example-group
        """
        document = yaml.safe_load(template_manifest)

        validator = SchemaValidator(validate.SCHEMAS)
        continue_running = validator.validate(document)

        self.assertTrue(continue_running)
        self.assertEquals(1, validator.error_counter)
        self.assertEquals(1, len(validator.messages))

        expect = ('JSON Schema Validation: Invalid document '
                  '[armada/Manifest/v1] example-manifest: \'release_prefix\' '
                  'is a required property.')
        err_msg = validator.messages[0]
        self.assertEquals(expect, err_msg.get('message'))

    def test_validate_validate_group_without_required_chart_group(self):
        template_group = """
        schema: armada/ChartGroup/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            description: this is sample
        """
        document = yaml.safe_load(template_group)

        validator = SchemaValidator(validate.SCHEMAS)
        continue_running = validator.validate(document)

        self.assertTrue(continue_running)
        self.assertEquals(1, validator.error_counter)
        self.assertEquals(1, len(validator.messages))

        expect = ('JSON Schema Validation: Invalid document '
                  '[armada/ChartGroup/v1] example-manifest: \'chart_group\' '
                  'is a required property.')
        err_msg = validator.messages[0]
        self.assertEquals(expect, err_msg.get('message'))

    def test_validate_chart_without_required_release_property(self):
        template_chart = """
        schema: armada/Chart/v1
        metadata:
          schema: metadata/Document/v1
          name: example-chart
        data:
          chart_name: keystone
          namespace: undercloud
          timeout: 100
          install:
            no_hooks: false
          upgrade:
            no_hooks: false
          values: {}
          source:
            type: git
            location: git://github.com/example/example
            subpath: example-chart
            reference: master
          dependencies:
            - dep-chart
        """
        document = yaml.safe_load(template_chart)

        validator = SchemaValidator(validate.SCHEMAS)
        continue_running = validator.validate(document)

        self.assertTrue(continue_running)
        self.assertEquals(1, validator.error_counter)
        self.assertEquals(1, len(validator.messages))

        expect = ('JSON Schema Validation: Invalid document '
                  '[armada/Chart/v1] example-chart: \'release\' '
                  'is a required property.')
        err_msg = validator.messages[0]
        self.assertEquals(expect, err_msg.get('message'))
