# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
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

from armada.utils import validate


class ValidateTestCase(unittest.TestCase):

    def setUp(self):
        super(ValidateTestCase, self).setUp()
        self.basepath = os.path.join(os.path.dirname(__file__))

    def _build_error_message(self, document, name, message):
        return "Invalid document [{}] {}: {}.".format(document, name, message)

    def test_validate_load_schemas(self):
        expected_schemas = [
            'armada/Chart/v1',
            'armada/ChartGroup/v1',
            'armada/Manifest/v1'
        ]
        for expected_schema in expected_schemas:
            self.assertIn(expected_schema, validate.SCHEMAS)

    def test_validate_armada_yaml_passes(self):
        template = '{}/templates/valid_armada_document.yaml'.format(
            self.basepath)

        with open(template) as f:
            document = yaml.safe_load_all(f.read())
        error_messages = validate.validate_armada_documents(document)

        self.assertFalse(error_messages)

    def test_validate_validate_manifest_passes(self):
        template_manifest = """
        schema: armada/Manifest/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            release_prefix: example
            chart_groups:
                - example-group
        """
        document = list(yaml.safe_load_all(template_manifest))
        is_valid, error = validate.validate_armada_document(document[0])

        self.assertTrue(is_valid)
        self.assertFalse(error)

    def test_validate_validate_group_passes(self):
        template_manifest = """
        schema: armada/ChartGroup/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            description: this is sample
            chart_group:
                - example-group
        """
        document = list(yaml.safe_load_all(template_manifest))
        is_valid, error = validate.validate_armada_document(document[0])

        self.assertTrue(is_valid)
        self.assertFalse(error)

    def test_validate_validate_chart_passes(self):
        template_manifest = """
        schema: armada/Chart/v1
        metadata:
          schema: metadata/Document/v1
          name: example-chart
        data:
          chart_name: keystone
          release: keystone
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
        document = list(yaml.safe_load_all(template_manifest))
        is_valid, error = validate.validate_armada_document(document[0])

        self.assertTrue(is_valid)
        self.assertFalse(error)


class ValidateNegativeTestCase(ValidateTestCase):

    def test_validate_load_duplicate_schemas_expect_runtime_error(self):
        """Validate that calling ``validate._load_schemas`` results in a 
        ``RuntimeError`` being thrown, because the call is made during module
        import, and importing the schemas again in manually results in
        duplicates.
        """
        with self.assertRaisesRegexp(
                RuntimeError,
                'Duplicate schema specified for: %s.' % 'armada/Chart/v1'):
            validate._load_schemas()

    def test_validate_no_dictionary_expect_type_error(self):
        expected_error = 'The provided input "invalid" must be a dictionary.'
        self.assertRaisesRegexp(TypeError, expected_error,
                                validate.validate_armada_documents,
                                ['invalid'])

    def test_validate_invalid_chart_armada_manifest(self):
        template = '{}/templates/invalid_chart_armada_document.yaml'.format(
            self.basepath)

        with open(template) as f:
            document = yaml.safe_load_all(f.read())
        error_messages = validate.validate_armada_documents(document)
        expected_error = self._build_error_message(
            'armada/Chart/v1', 'mariadb',
            "'release' is a required property")

        self.assertEqual(1, len(error_messages))
        self.assertEqual(expected_error, error_messages[0])

    def test_validate_validate_group_without_required_chart_group(self):
        template_manifest = """
        schema: armada/ChartGroup/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            description: this is sample
        """
        document = yaml.safe_load(template_manifest)
        is_valid, error = validate.validate_armada_document(document)

        expected_error = self._build_error_message(
            'armada/ChartGroup/v1', 'example-manifest',
            "'chart_group' is a required property")

        self.assertFalse(is_valid)
        self.assertEqual(error, expected_error)

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
        is_valid, error = validate.validate_armada_document(document)
        expected_error = self._build_error_message(
            'armada/Manifest/v1', 'example-manifest',
            "'release_prefix' is a required property")

        self.assertFalse(is_valid)
        self.assertEqual(error, expected_error)

    def test_validate_chart_without_required_release_property(self):
        template_manifest = """
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
        document = yaml.safe_load(template_manifest)
        is_valid, error = validate.validate_armada_document(document)
        expected_error = self._build_error_message(
            'armada/Chart/v1', 'example-chart',
            "'release' is a required property")

        self.assertFalse(is_valid)
        self.assertEqual(error, expected_error)
