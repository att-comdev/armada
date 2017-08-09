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

import unittest
import yaml

from armada.handlers.override import Override
from armada import const


class OverrideTestCase(unittest.TestCase):

    base_documents = """
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
        location: https://github.com/namespace/hello-world-chart
        subpath: .
        reference: master
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
    """

    def test_find_document_type_valid(self):
        ovr = Override(self.base_documents)
        test_group = ovr.find_document_type('chart_group')
        self.assertEqual(test_group, const.DOCUMENT_GROUP)

        test_chart = ovr.find_document_type('chart')
        self.assertEqual(test_chart, const.DOCUMENT_CHART)

        test_manifest = ovr.find_document_type('manifest')
        self.assertEqual(test_manifest, const.DOCUMENT_MANIFEST)

    def test_find_document_type_invalid(self):
        with self.assertRaises(Exception):
            ovr = Override(self.base_documents)
            ovr.find_document_type('charts')

    @unittest.skip("a")
    def test_update_dictionary_valid(self):
        manifest_change = """
        ---
        schema: armada/Chart/v1
        metadata:
          schema: metadata/Document/v1
          name: blog-1
        data:
          chart_name: blog-1
          release: blog-1
          namespace: blog-blog
          values: {}
          source:
            type: dev
        """

        expected_document = """
        ---
        schema: armada/Chart/v1
        metadata:
          schema: metadata/Document/v1
          name: blog-1
        data:
          chart_name: blog-1
          release: blog-1
          namespace: blog-blog
          values: {}
          source:
            type: dev
            location: https://github.com/namespace/hello-world-chart
            subpath: .
            reference: master
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
        """

        merging_values = yaml.load_all(manifest_change)
        ovr = Override(self.base_documents).update_document(merging_values)
        expect_doc = yaml.load_all(expected_document)
        self.assertEqual(ovr, expect_doc)

    def test_update_dictionary_invalid(self):
        pass

    @unittest.skip("a")
    def test_find_manifest_document_valid(self):

        doc_path = ['chart', 'blog-1']
        doc_obj = list(yaml.safe_load_all(self.base_documents))
        ovr = Override(doc_obj).find_manifest_document(
            doc_path)
        expected_doc = yaml.safe_load_all("""
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
            location: https://github.com/namespace/hello-world-chart
            subpath: .
            reference: master
          dependencies: []
        """)

        self.assertEqual(ovr, expected_doc)

    def test_find_manifest_document_invalid(self):
        pass

    def test_convert_array_to_dict_valid(self):
        data_path = ['a', 'b', 'c']
        new_value = "dev"
        expected_dict = {
            'a': {
                'b': {
                    'c': 'dev'
                }
            }
        }

        ovr = Override(self.base_documents).array_to_dict(data_path, new_value)
        self.assertEqual(ovr, expected_dict)

    def test_convert_array_to_dict_invalid(self):
        data_path = ['a', 'b', 'c']
        new_value = ""

        ovr = Override(self.base_documents).array_to_dict(data_path, new_value)
        self.assertIsNone(ovr)

        ovr = Override(self.base_documents).array_to_dict([], new_value)
        self.assertIsNone(ovr)

    def test_override_manifest_value(self):
        pass

    def test_override_manifest_invalue(self):
        pass
