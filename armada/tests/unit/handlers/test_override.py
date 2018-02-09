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
        originalCopy = "{}/templates/override-{}.yaml". \
            format(self.basepath, '01')
        values_yaml = "{}/templates/override-{}-expected.yaml".format(
            self.basepath, '01')
        self.base_manifest = '{}/templates/base.yaml'. \
            format(self.basepath)
        with open(original) as f, open(originalCopy) as g:
                originalDocuments = list(yaml.safe_load_all(f.read()))
                documentsCopy = list(yaml.safe_load_all(g.read()))
                ovr = Override(originalDocuments, None, [values_yaml])
                ovr.update_manifests()
                # addition of the values changes the original document
                self.assertNotEqual(originalDocuments, documentsCopy)
                # verifying that these documents have the same value now
                valuesDocument = list(yaml.safe_load_all(
                    open(values_yaml).read()))
                self.assertEqual(originalDocuments, valuesDocument)

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

    def test_update_chart_group_document_valid(self):
        examples_dir = os.path.join(
            os.getcwd(), 'armada', 'tests', 'unit', 'resources')
        with open(os.path.join(examples_dir, 'keystone-manifest.yaml')) as f:
            documents = list(yaml.safe_load_all(f.read()))
            ovr = Override(documents)
            ovr.update_chart_group_document(documents[5])

    def test_update_armada_manifest_valid(self):
        examples_dir = os.path.join(
            os.getcwd(), 'armada', 'tests', 'unit', 'resources')
        with open(os.path.join(examples_dir, 'keystone-manifest.yaml')) as f:
            documents = list(yaml.safe_load_all(f.read()))
            ovr = Override(documents)
            ovr.update_armada_manifest(documents[6])

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
