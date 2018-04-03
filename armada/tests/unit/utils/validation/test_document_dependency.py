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

import testtools

from armada.tests.unit import base


class BaseManifestDocumentsValidatorTest(base.ArmadaTestCase):
    def setUp(self):
        super(BaseManifestDocumentsValidatorTest, self).setUp()
        # self.manifest = [yaml.safe_load(manifest1)]
        # self.group = [yaml.safe_load(group1)]
        # self.chart = [yaml.safe_load(chart1)]


class ManifestDocumentsValidatorTestCase(BaseManifestDocumentsValidatorTest):

    @testtools.skip('WIP')
    def test_validate(self):
        self.assertTrue(True)
        # validator = ManifestStructureValidator()
        # validator.validate(self.chart, self.group, self.manifest, None)

        # self.assertEquals(len(validator.messages), 0)
        # self.assertEquals(validator.error_counter, 0)

    @testtools.skip('WIP')
    def test_validate_negative(self):
        self.assertTrue(True)
        # validator = ManifestStructureValidator()
        # validator.validate([], self.group, self.manifest, None)

        # self.assertEquals(len(validator.messages), 1)
        # self.assertEquals(validator.error_counter, 1)

        # expect = ('Manifest should be a list of documents that includes at '
        #         'least one of each armada/Chart/v1 and armada/ChartGroup/v1,'
        #           ' and exactly one armada/Manifest/v1.')
        # err_msg = validator.messages[0]
        # self.assertEquals(err_msg.get('diagnostic'), expect)

    @testtools.skip('WIP')
    def test_validate_negative_no_manifest_no_target(self):
        self.assertTrue(True)
        # validator = ManifestStructureValidator()
        # validator.validate(self.chart, self.group, [], None)

        # self.assertEquals(len(validator.messages), 1)
        # self.assertEquals(validator.error_counter, 1)

        # expect = ('Manifest should be a list of documents that includes at '
        #         'least one of each armada/Chart/v1 and armada/ChartGroup/v1,'
        #           ' and exactly one armada/Manifest/v1.')
        # err_msg = validator.messages[0]
        # self.assertEquals(err_msg.get('diagnostic'), expect)

    @testtools.skip('WIP')
    def test_validate_negative_no_manifest_with_target(self):
        self.assertTrue(True)
        # target = 'TARGET'

        # validator = ManifestStructureValidator()
        # validator.validate(self.chart, self.group, [], target)

        # self.assertEquals(len(validator.messages), 1)
        # self.assertEquals(validator.error_counter, 1)

        # expect = ('Manifest should be a list of documents that includes at '
        #         'least one of each armada/Chart/v1 and armada/ChartGroup/v1,'
        #           ' and exactly one armada/Manifest/v1. Did you specify the '
        #           'wrong target (%s)?' % target)
        # err_msg = validator.messages[0]
        # self.assertEquals(err_msg.get('diagnostic'), expect)
