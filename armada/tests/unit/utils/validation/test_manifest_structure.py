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
from armada.handlers.manifest import Manifest
from armada.utils.validation.manifest_structure import \
    ManifestStructureValidator


manifest1 = """
schema: armada/Manifest/v1
metadata:
    schema: metadata/Document/v1
    name: example-manifest
data:
    release_prefix: example
    chart_groups:
        - example-group
"""

group1 = """
schema: armada/ChartGroup/v1
metadata:
  schema: metadata/Document/v1
  name: example-group
data:
  description: "Example group"
  sequenced: False
  test_charts: False
  chart_group:
    - example-chart
"""

chart1 = """
schema: armada/Chart/v1
metadata:
  schema: metadata/Document/v1
  name: example-chart
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


class BaseManifestStructureValidatorTest(base.ArmadaTestCase):
    def setUp(self):
        super(BaseManifestStructureValidatorTest, self).setUp()


class ManifestStructureValidatorTestCase(BaseManifestStructureValidatorTest):

    def test_validate(self):
        docs = '%s---%s---%s' % (chart1, group1, manifest1)
        manifest = Manifest(list(yaml.load_all(docs)))

        validator = ManifestStructureValidator()
        validator.validate(manifest, None)

        self.assertEquals(len(validator.messages), 0)
        self.assertEquals(validator.error_counter, 0)

    def test_validate_negative(self):
        docs = '%s---%s' % (group1, manifest1)
        manifest = Manifest(list(yaml.load_all(docs)))

        validator = ManifestStructureValidator()
        validator.validate(manifest, None)

        self.assertEquals(len(validator.messages), 1)
        self.assertEquals(validator.error_counter, 1)

        expect = ('Manifest should be a list of documents that includes at '
                  'least one of each armada/Chart/v1 and armada/ChartGroup/v1,'
                  ' and exactly one armada/Manifest/v1.')
        err_msg = validator.messages[0]
        self.assertEquals(err_msg.get('diagnostic'), expect)

    def test_validate_negative_no_manifest_no_target(self):
        docs = '%s---%s' % (chart1, group1)
        manifest = Manifest(list(yaml.load_all(docs)))

        validator = ManifestStructureValidator()
        validator.validate(manifest, None)

        self.assertEquals(len(validator.messages), 1)
        self.assertEquals(validator.error_counter, 1)

        expect = ('Manifest should be a list of documents that includes at '
                  'least one of each armada/Chart/v1 and armada/ChartGroup/v1,'
                  ' and exactly one armada/Manifest/v1.')
        err_msg = validator.messages[0]
        self.assertEquals(err_msg.get('diagnostic'), expect)

    def test_validate_negative_no_manifest_with_target(self):
        docs = '%s---%s' % (chart1, group1)
        manifest = Manifest(list(yaml.load_all(docs)))
        target = 'TARGET'

        validator = ManifestStructureValidator()
        validator.validate(manifest, target)

        self.assertEquals(len(validator.messages), 1)
        self.assertEquals(validator.error_counter, 1)

        expect = ('Manifest should be a list of documents that includes at '
                  'least one of each armada/Chart/v1 and armada/ChartGroup/v1,'
                  ' and exactly one armada/Manifest/v1. Did you specify the '
                  'wrong target (%s)?' % target)
        err_msg = validator.messages[0]
        self.assertEquals(err_msg.get('diagnostic'), expect)
