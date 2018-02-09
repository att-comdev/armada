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
import yaml
import os
import copy

from armada.handlers.override import Override
from armada.exceptions import override_exceptions
from armada import const


class OverrideTestCase(testtools.TestCase):
    def setUp(self):
        super(OverrideTestCase, self).setUp()
        self.basepath = os.path.join(os.path.dirname(__file__))
        self.base_manifest = '{}/templates/base.yaml'.format(self.basepath)

    def test_update_manifests_no_overrides_and_values_valid(self):
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))
            ovr = Override(documents)
            ovr.update_manifests()
            # no updates since no overrides and values provided
            self.assertEqual(documents, ovr.documents)

    def test_update_manifests_with_values_valid(self):
        original = "{}/templates/override-{}.yaml".format(self.basepath, '01')
        values_yaml = "{}/templates/override-{}-expected.yaml".format(
            self.basepath, '01')
        with open(original) as f, open(values_yaml) as g:
            original_documents = list(yaml.safe_load_all(f.read()))
            documents_copy = copy.deepcopy(original_documents)
            values_documents = list(yaml.safe_load_all(g.read()))
        ovr = Override(original_documents, None, [values_yaml])
        ovr.update_manifests()
        # updating values changed the original document
        self.assertNotEqual(original_documents, documents_copy)
        # verifying that these documents have the same value now
        self.assertEqual(original_documents, values_documents)

    def test_update_manifests_with_values_and_overrides_valid(self):
        values_yaml = "{}/templates/override-{}-expected.yaml".format(
            self.basepath, '01')
        comparison_yaml = "{}/templates/override-{}-expected.yaml".format(
            self.basepath, '03')

        with open(self.base_manifest) as f, open(values_yaml) as g:
            original_documents = list(yaml.safe_load_all(f.read()))
            documents_copy = copy.deepcopy(original_documents)
            values_documents = list(yaml.safe_load_all(g.read()))
        override = ('manifest:simple-armada:chart_groups=\
            blog-group3,blog-group4',)

        ovr = Override(original_documents, override, [values_yaml])
        ovr.update_manifests()
        # updating values changed the original document
        self.assertNotEqual(original_documents, documents_copy)
        # since overrides done, these documents aren't same anymore
        self.assertNotEqual(original_documents, values_documents)
        with open(comparison_yaml) as c:
            comparison_documents = list(yaml.safe_load_all(c.read()))
        # verifying that the override is correct
        self.assertEqual(original_documents[2]['data']['chart_groups'],
                         comparison_documents[0]['data']['chart_groups'])

    def test_load_yaml_file(self):
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))
            ovr = Override(documents)
            value = ovr._load_yaml_file(self.base_manifest)
            self.assertIsInstance(value, list)

    def test_find_document_type_valid(self):
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))
            ovr = Override(documents)
            test_group = ovr.find_document_type('chart_group')
            self.assertEqual(test_group, const.DOCUMENT_GROUP)

            test_chart = ovr.find_document_type('chart')
            self.assertEqual(test_chart, const.DOCUMENT_CHART)

            test_manifest = ovr.find_document_type('manifest')
            self.assertEqual(test_manifest, const.DOCUMENT_MANIFEST)

    def test_update_chart_document_valid(self):
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))
        documents_modified = copy.deepcopy(documents)

        # Case 1: Checking if primitives get updated
        documents_modified[0]['data']['chart_name'] = 'modified'

        # starting out, both doc have different values for data
        self.assertNotEqual(documents[0], documents_modified[0])

        ovr = Override(documents)
        # update with document values from modified file
        ovr.update_chart_document(documents_modified[0])

        # after the update, both documents are equal
        self.assertEqual(ovr.documents[0]['data']['chart_name'],
                         documents_modified[0]['data']['chart_name'])
        self.assertEqual(ovr.documents[0], documents_modified[0])

        # Case 2: Checking if dictionaries get updated
        documents_modified[0]['data']['values'] = {'foo': 'bar'}

        ovr.update_chart_document(documents_modified[0])

        # after the update, both documents are equal
        self.assertEqual(ovr.documents[0]['data']['values'],
                         documents_modified[0]['data']['values'])
        self.assertEqual(ovr.documents[0], documents_modified[0])

        # Case 3: Checking if lists get updated
        documents_modified[0]['data']['dependencies'] = ['foo', 'bar']

        ovr.update_chart_document(documents_modified[0])

        # after the update, both documents are equal
        self.assertEqual(['foo', 'bar'],
                         ovr.documents[0]['data']['dependencies'])
        self.assertEqual(documents_modified[0]['data']['dependencies'],
                         ovr.documents[0]['data']['dependencies'])
        self.assertEqual(ovr.documents[0], documents_modified[0])

    def test_update_chart_document_keys_not_removed_with_override(self):
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))

        documents_modified = copy.deepcopy(documents)
        del documents_modified[0]['data']['chart_name']

        # starting out, both doc have different values for data
        self.assertNotEqual(documents[0], documents_modified[0])

        ovr = Override(documents)
        # update with document values from base_manifest
        ovr.update_chart_document(documents_modified[0])

        self.assertIn('chart_name', ovr.documents[0]['data'])
        self.assertNotEqual(ovr.documents[0], documents_modified[0])

    def test_update_chart_group_document_valid(self):
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))
        documents_modified = copy.deepcopy(documents)
        documents_modified[1]['data']['sequenced'] = True

        # starting out, both doc have different values for data
        self.assertNotEqual(documents[1], documents_modified[1])

        ovr = Override(documents)
        # update with document values from modified file
        ovr.update_chart_group_document(documents_modified[1])

        # after the update, both documents are equal
        self.assertEqual(ovr.documents[1]['data']['sequenced'],
                         documents_modified[1]['data']['sequenced'])
        self.assertEqual(ovr.documents[1], documents_modified[1])

    def test_update_chart_group_document_keys_not_removed_with_override(self):
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))

        documents_modified = copy.deepcopy(documents)
        del documents_modified[1]['data']['sequenced']

        # starting out, both doc have different values for data
        self.assertNotEqual(documents[1], documents_modified[1])

        ovr = Override(documents)
        # update with document values from base_manifest
        ovr.update_chart_group_document(documents_modified[1])

        self.assertIn('sequenced', ovr.documents[1]['data'])
        self.assertNotEqual(ovr.documents[1], documents_modified[1])

    def test_update_armada_manifest_valid(self):
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))
        documents_modified = copy.deepcopy(documents)
        documents_modified[2]['data']['release_prefix'] = 'armada-modified'

        # starting out, both doc have different values for data
        self.assertNotEqual(documents[2], documents_modified[2])

        ovr = Override(documents)
        # update with document values from modified file
        ovr.update_armada_manifest(documents_modified[2])

        # after the update, both documents are equal
        self.assertEqual(ovr.documents[2]['data']['release_prefix'],
                         documents_modified[2]['data']['release_prefix'])
        self.assertEqual(ovr.documents[2], documents_modified[2])

    def test_update_armada_manifest_keys_not_removed_with_override(self):
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))

        documents_modified = copy.deepcopy(documents)
        del documents_modified[2]['data']['release_prefix']

        # starting out, both doc have different values for data
        self.assertNotEqual(documents[2], documents_modified[2])

        ovr = Override(documents)
        # update with document values from base_manifest
        ovr.update_armada_manifest(documents_modified[2])

        self.assertIn('release_prefix', ovr.documents[2]['data'])
        self.assertNotEqual(ovr.documents[2], documents_modified[2])

    def test_update_dictionary_valid(self):
        expected = "{}/templates/override-{}-expected.yaml".format(
            self.basepath, '01')
        merge = "{}/templates/override-{}.yaml".format(self.basepath, '01')

        with open(self.base_manifest) as f, open(expected) as e, open(
                merge) as m:
            merging_values = list(yaml.safe_load_all(m.read()))
            documents = list(yaml.safe_load_all(f.read()))
            doc_path = ['chart', 'blog-1']
            ovr = Override(documents)
            ovr.update_document(merging_values)
            ovr_doc = ovr.find_manifest_document(doc_path)
            expect_doc = list(yaml.load_all(e.read()))[0]

            self.assertEqual(ovr_doc, expect_doc)

    def test_set_list_valid(self):
        expected = "{}/templates/override-{}-expected.yaml".format(
            self.basepath, '03')

        with open(self.base_manifest) as f, open(expected) as e:
            documents = list(yaml.safe_load_all(f.read()))
            doc_path = ['manifest', 'simple-armada']
            override = ('manifest:simple-armada:chart_groups=\
                         blog-group3,blog-group4',)
            ovr = Override(documents, override)
            ovr.update_manifests()
            ovr_doc = ovr.find_manifest_document(doc_path)
            expect_doc = list(yaml.load_all(e.read()))[0]
            self.assertEqual(expect_doc, ovr_doc)

    def test_find_manifest_document_valid(self):
        expected = "{}/templates/override-{}-expected.yaml".format(
            self.basepath, '02')

        with open(self.base_manifest) as f, open(expected) as e:
            doc_path = ['chart', 'blog-1']
            documents = list(yaml.safe_load_all(f.read()))
            ovr = Override(documents).find_manifest_document(doc_path)
            expected_doc = list(yaml.safe_load_all(e.read()))[0]

            self.assertEqual(ovr, expected_doc)

    def test_convert_array_to_dict_valid(self):
        data_path = ['a', 'b', 'c']
        new_value = "dev"
        expected_dict = {'a': {'b': {'c': 'dev'}}}

        ovr = Override(self.base_manifest).array_to_dict(data_path, new_value)
        self.assertEqual(ovr, expected_dict)


class OverrideNegativeTestCase(testtools.TestCase):
    def setUp(self):
        super(OverrideNegativeTestCase, self).setUp()
        self.basepath = os.path.join(os.path.dirname(__file__))
        self.base_manifest = '{}/templates/base.yaml'.format(self.basepath)

    def test_update_manifests_invalid(self):
        missing_yaml = "{}/templates/non_existing_yaml.yaml". \
            format(self.basepath)
        with open(self.base_manifest):
            ovr = Override(missing_yaml)
            self.assertRaises(
                override_exceptions.InvalidOverrideValueException,
                ovr.update_manifests)

    def test_load_yaml_file_invalid(self):
        missing_yaml = "{}/templates/non_existing_yaml.yaml". \
            format(self.basepath)
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))
            ovr = Override(documents)
            self.assertRaises(override_exceptions.InvalidOverrideFileException,
                              ovr._load_yaml_file, missing_yaml)

    def test_find_document_type_invalid(self):
        with open(self.base_manifest) as f:
            documents = list(yaml.safe_load_all(f.read()))
            ovr = Override(documents)
            self.assertRaises(ValueError, ovr.find_document_type,
                              'non_existing_document')

    def test_convert_array_to_dict_invalid(self):
        data_path = ['a', 'b', 'c']
        new_value = ""

        ovr = Override(self.base_manifest).array_to_dict(data_path, new_value)
        self.assertIsNone(ovr)

        ovr = Override(self.base_manifest).array_to_dict([], new_value)
        self.assertIsNone(ovr)
