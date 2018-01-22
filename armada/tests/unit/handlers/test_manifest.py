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

import testtools

from armada import const
from armada.handlers import manifest


class ManifestTestCase(testtools.TestCase):

    def test_get_documents(self):
        documents = [
            {
                'schema': const.DOCUMENT_CHART
            },
            {
                'schema': const.DOCUMENT_CHART
            },
            {
                'schema': const.DOCUMENT_GROUP
            },
            {
                'schema': const.DOCUMENT_GROUP
            },
            {
                'schema': const.DOCUMENT_MANIFEST
            }
        ]
        armada_manifest = manifest.Manifest(documents)

        self.assertIsInstance(armada_manifest.charts, list)
        self.assertIsInstance(armada_manifest.groups, list)
        self.assertIsNotNone(armada_manifest.manifest)
        self.assertEqual([documents[x] for x in range(2)],
                         armada_manifest.charts)
        self.assertEqual([documents[x] for x in range(2, 4)],
                         armada_manifest.groups)
        self.assertEqual(documents[4], armada_manifest.manifest)
