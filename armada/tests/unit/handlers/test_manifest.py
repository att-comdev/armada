# Copyright 2017 The Armada Authors.
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

import os
import yaml

import testtools

from armada import const
from armada.handlers import manifest


class ManifestTestCase(testtools.TestCase):

    def setUp(self):
        super(ManifestTestCase, self).setUp()
        examples_dir = os.path.join(
            os.getcwd(), 'armada', 'tests', 'unit', 'resources')
        with open(os.path.join(examples_dir, 'keystone-manifest.yaml')) as f:
            self.documents = list(yaml.safe_load_all(f.read()))

    def test_get_documents(self):
        armada_manifest = manifest.Manifest(self.documents)

        self.assertIsInstance(armada_manifest.charts, list)
        self.assertIsInstance(armada_manifest.groups, list)
        self.assertIsNotNone(armada_manifest.manifest)

        self.assertEqual(4, len(armada_manifest.charts))
        self.assertEqual(2, len(armada_manifest.groups))

        self.assertEqual([self.documents[x] for x in range(4)],
                         armada_manifest.charts)
        self.assertEqual([self.documents[x] for x in range(4, 6)],
                         armada_manifest.groups)
        self.assertEqual(self.documents[-1], armada_manifest.manifest)

    def test_find_chart_document(self):
        armada_manifest = manifest.Manifest(self.documents)
        chart = armada_manifest.find_chart_document('helm-toolkit')
        self.assertEqual(self.documents[0], chart)

    def test_find_group_document(self):
        armada_manifest = manifest.Manifest(self.documents)
        chart = armada_manifest.find_chart_group_document('openstack-keystone')
        self.assertEqual(self.documents[-2], chart)


class ManifestNegativeTestCase(testtools.TestCase):

    def setUp(self):
        super(ManifestNegativeTestCase, self).setUp()
        examples_dir = os.path.join(
            os.getcwd(), 'armada', 'tests', 'unit', 'resources')
        with open(os.path.join(examples_dir, 'keystone-manifest.yaml')) as f:
            self.documents = list(yaml.safe_load_all(f.read()))

    def test_find_chart_document_negative(self):
        armada_manifest = manifest.Manifest(self.documents)
        error_re = r'Could not find a %s named "%s"' % (
            const.DOCUMENT_CHART, 'invalid')
        self.assertRaisesRegexp(ValueError, error_re,
                                armada_manifest.find_chart_document, 'invalid')

    def test_find_group_document_negative(self):
        armada_manifest = manifest.Manifest(self.documents)
        error_re = r'Could not find a %s named "%s"' % (
            const.DOCUMENT_GROUP, 'invalid')
        self.assertRaisesRegexp(ValueError, error_re,
                                armada_manifest.find_chart_group_document,
                                'invalid')
