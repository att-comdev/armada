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

from armada.utils import validate


class ValidateTestCase(unittest.TestCase):

    def setUp(self):
        self.basepath = os.path.join(os.path.dirname(__file__))

    def error_message(self, document, name, message):
        return "Invalid Document [{}] {}: {}".format(document, name, message)

    def test_validate_armada_yaml_pass(self):
        template = '{}/templates/valid_armada_document.yaml'.format(
            self.basepath)

        with open(template) as f:
            document = yaml.safe_load_all(f.read())
            resp = validate.validate_armada_documents(document)

            assert type(resp) is not list
            self.assertTrue(resp)

    def test_validate_invalid_chart_armada_manifest(self):
        template = '{}/templates/invalid_chart_armada_document.yaml'.format(
            self.basepath)

        with open(template) as f:
            document = yaml.safe_load_all(f.read())
            resp = validate.validate_armada_documents(document)
            expected_error = self.error_message(
                'armada/Chart/v1', 'mariadb',
                "'release' is a required property")

            self.assertTrue(resp)

            self.assertEqual(resp[0], expected_error)

    def test_validate_validate_manifest_pass(self):
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
        resp, err = validate.validate_armada_document(document[0])

        self.assertFalse(err)
        self.assertTrue(resp)

        assert validate.validate_armada_document('') is None
        assert validate.validate_armada_document({})[1] is None

    def test_validate_validate_manifest_no_prefix(self):
        template_manifest = """
        schema: armada/Manifest/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            chart_groups:
                - example-group
        """
        document = list(yaml.safe_load_all(template_manifest))
        resp, err = validate.validate_armada_document(document[0])

        expected_error = self.error_message(
            'armada/Manifest/v1', 'example-manifest',
            "'release_prefix' is a required property")

        self.assertFalse(resp)
        self.assertEqual(err, expected_error)

    def test_validate_validate_group_pass(self):
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
        resp, err = validate.validate_armada_document(document[0])

        self.assertTrue(resp)
        self.assertFalse(err)

    def test_validate_validate_group_no_chart_group(self):
        template_manifest = """
        schema: armada/ChartGroup/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            description: this is sample
        """
        document = list(yaml.safe_load_all(template_manifest))
        resp, err = validate.validate_armada_document(document[0])

        expected_error = self.error_message(
            'armada/ChartGroup/v1', 'example-manifest',
            "'chart_group' is a required property")

        self.assertTrue(err)
        self.assertFalse(resp)

        self.assertEqual(err, expected_error)

    def test_validate_validate_chart_pass(self):
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
        resp, err = validate.validate_armada_document(document[0])

        self.assertFalse(err)
        self.assertTrue(resp)

    def test_validate_validate_chart_no_release(self):
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
        document = list(yaml.safe_load_all(template_manifest))
        resp, err = validate.validate_armada_document(document[0])

        self.assertFalse(resp)
        expected_error = self.error_message(
            'armada/Chart/v1', 'example-chart',
            "'release' is a required property")

        self.assertEqual(err, expected_error)

    def test_validate_load_schemas(self):
        self.assertIsNotNone(validate.SCHEMAS.get('armada/Chart/v1', None))
        self.assertIsNotNone(
            validate.SCHEMAS.get('armada/ChartGroup/v1', None))
        self.assertIsNotNone(validate.SCHEMAS.get('armada/Manifest/v1', None))

        with self.assertRaises(RuntimeError):
            validate._load_schemas()
