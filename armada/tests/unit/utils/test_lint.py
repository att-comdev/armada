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

from armada.utils import lint

class LintTestCase(unittest.TestCase):

    def setUp(self):
        self.basepath = os.path.join(os.path.dirname(__file__))

    def test_lint_armada_yaml_pass(self):
        template = '{}/templates/valid_armada_document.yaml'.format(
            self.basepath)
        document = yaml.safe_load_all(open(template).read())
        resp = lint.validate_armada_documents(document)
        self.assertTrue(resp)

    def test_lint_armada_manifest_no_groups(self):
        template_manifest = """
        schema: armada/Manifest/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            release_prefix: example
        """
        document = yaml.safe_load_all(template_manifest)
        with self.assertRaises(Exception):
            lint.validate_armada_documents(document)

    def test_lint_validate_manifest_pass(self):
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
        document = yaml.safe_load_all(template_manifest)
        self.assertTrue(lint.validate_manifest_document(document))

    def test_lint_validate_manifest_no_prefix(self):
        template_manifest = """
        schema: armada/Manifest/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            chart_groups:
                - example-group
        """
        document = yaml.safe_load_all(template_manifest)
        with self.assertRaises(Exception):
            lint.validate_manifest_document(document)

    def test_lint_validate_group_pass(self):
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
        document = yaml.safe_load_all(template_manifest)
        self.assertTrue(lint.validate_chart_group_document(document))

    def test_lint_validate_group_no_chart_group(self):
        template_manifest = """
        schema: armada/ChartGroup/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            description: this is sample
        """
        document = yaml.safe_load_all(template_manifest)
        with self.assertRaises(Exception):
            lint.validate_chart_group_document(document)

    def test_lint_validate_chart_pass(self):
        template_manifest = """
        schema: armada/Chart/v1
        metadata:
          schema: metadata/Document/v1
          name: example-chart
        data:
          name: keystone
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
        document = yaml.safe_load_all(template_manifest)
        self.assertTrue(lint.validate_chart_document(document))

    def test_lint_validate_chart_no_release(self):
        template_manifest = """
        schema: armada/Chart/v1
        metadata:
          schema: metadata/Document/v1
          name: example-chart
        data:
          name: keystone
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
        document = yaml.safe_load_all(template_manifest)
        with self.assertRaises(Exception):
            lint.validate_chart_document(document)
