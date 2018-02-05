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
import os

from armada.handlers.override import Override
from armada import const


class OverrideTestCase(unittest.TestCase):
    def setUp(self):
        self.basepath = os.path.join(os.path.dirname(__file__))
        self.base_manifest = '{}/templates/base.yaml'.format(self.basepath)

    def test_load_yaml_file(self):
        with open(self.base_manifest) as f:
            doc_obj = list(yaml.safe_load_all(f.read()))
            ovr = Override(doc_obj)
            value = ovr._load_yaml_file(self.base_manifest)
            self.assertIsInstance(value, list)

    def test_find_document_type_valid(self):
        with open(self.base_manifest) as f:
            doc_obj = list(yaml.safe_load_all(f.read()))
            ovr = Override(doc_obj)
            test_group = ovr.find_document_type('chart_group')
            self.assertEqual(test_group, const.DOCUMENT_GROUP)

            test_chart = ovr.find_document_type('chart')
            self.assertEqual(test_chart, const.DOCUMENT_CHART)

            test_manifest = ovr.find_document_type('manifest')
            self.assertEqual(test_manifest, const.DOCUMENT_MANIFEST)

    def test_find_document_type_invalid(self):
        with self.assertRaises(Exception):
            with open(self.base_manifest) as f:
                doc_obj = list(yaml.safe_load_all(f.read()))
                ovr = Override(doc_obj)
                ovr.find_document_type('charts')

    def test_update_dictionary_valid(self):
        expected = "{}/templates/override-{}-expected.yaml".format(
            self.basepath, '01')
        merge = "{}/templates/override-{}.yaml".format(self.basepath, '01')

        with open(self.base_manifest) as f, open(expected) as e, open(
                merge) as m:
            merging_values = list(yaml.safe_load_all(m.read()))
            doc_obj = list(yaml.safe_load_all(f.read()))
            doc_path = ['chart', 'blog-1']
            ovr = Override(doc_obj)
            ovr.update_document(merging_values)
            ovr_doc = ovr.find_manifest_document(doc_path)
            expect_doc = list(yaml.load_all(e.read()))[0]

            self.assertEqual(ovr_doc, expect_doc)

    def test_set_list_valid(self):
        expected = "{}/templates/override-{}-expected.yaml".format(
            self.basepath, '03')

        with open(self.base_manifest) as f, open(expected) as e:
            doc_obj = list(yaml.safe_load_all(f.read()))
            doc_path = ['manifest', 'simple-armada']
            override = ('manifest:simple-armada:chart_groups=\
                         blog-group3,blog-group4',)
            ovr = Override(doc_obj, override)
            ovr.update_manifests()
            ovr_doc = ovr.find_manifest_document(doc_path)
            expect_doc = list(yaml.load_all(e.read()))[0]
            self.assertEqual(expect_doc, ovr_doc)

    def test_find_manifest_document_valid(self):
        expected = "{}/templates/override-{}-expected.yaml".format(
            self.basepath, '02')

        with open(self.base_manifest) as f, open(expected) as e:
            doc_path = ['chart', 'blog-1']
            doc_obj = list(yaml.safe_load_all(f.read()))
            ovr = Override(doc_obj).find_manifest_document(doc_path)
            expected_doc = list(yaml.safe_load_all(e.read()))[0]

            self.assertEqual(ovr, expected_doc)

    def test_convert_array_to_dict_valid(self):
        data_path = ['a', 'b', 'c']
        new_value = "dev"
        expected_dict = {'a': {'b': {'c': 'dev'}}}

        ovr = Override(self.base_manifest).array_to_dict(data_path, new_value)
        self.assertEqual(ovr, expected_dict)

    def test_convert_array_to_dict_invalid(self):
        data_path = ['a', 'b', 'c']
        new_value = ""

        ovr = Override(self.base_manifest).array_to_dict(data_path, new_value)
        self.assertIsNone(ovr)

        ovr = Override(self.base_manifest).array_to_dict([], new_value)
        self.assertIsNone(ovr)
