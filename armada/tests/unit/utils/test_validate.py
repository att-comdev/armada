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

import os
import yaml

import testtools

from armada.tests.unit import base
from armada.utils import validate


template_chart = """
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
  dependencies: []
"""

template_chart_group = """
schema: armada/ChartGroup/v1
metadata:
    schema: metadata/Document/v1
    name: example-manifest
data:
    description: this is sample
    chart_group:
        - example-chart
"""

template_manifest = """
schema: armada/Manifest/v1
metadata:
    schema: metadata/Document/v1
    name: example-manifest
data:
    release_prefix: example
    chart_groups:
        - example-chart
"""


class BaseValidateTest(base.ArmadaTestCase):

    def setUp(self):
        super(BaseValidateTest, self).setUp()
        self.basepath = os.path.join(os.path.dirname(__file__), os.pardir)

    def _build_error_message(self, document, name, message):
        return "Invalid document [{}] {}: {}.".format(document, name, message)


class ValidateOwnExamplesTestCase(BaseValidateTest):
    """Validates that each of the relevant example documents under
    ``armada/examples`` passes internal Armada schema validation.

    """

    def test_own_document_examples(self):
        examples_path = os.path.join(os.getcwd(), 'examples')
        example_files = [
            os.path.join(examples_path, f) for f in os.listdir(examples_path)
            if os.path.isfile(os.path.join(examples_path, f))
        ]
        validated_manifests = []

        for example_file in example_files:
            with open(example_file) as f:
                documents = yaml.safe_load_all(f.read())

            # If the example file doesn't have a document with
            # armada/Manifest/v1 then skip validating it as the example could
            # merely be an override.
            has_manifest = any(
                x['schema'] == 'armada/Manifest/v1' for x in documents)
            if not has_manifest:
                continue

            validated_manifests.append(example_file)
            valid, _ = validate.validate_armada_documents(list(documents))
            self.assertTrue(valid)

        self.assertTrue(validated_manifests)


class ValidateTestCase(BaseValidateTest):

    def test_validate_load_schemas(self):
        expected_schemas = [
            'armada/Chart/v1',
            'armada/ChartGroup/v1',
            'armada/Manifest/v1'
        ]
        for expected_schema in expected_schemas:
            self.assertIn(expected_schema, validate.SCHEMAS)

    def test_validate_armada_yaml_passes(self):
        template = '{}/resources/valid_armada_document.yaml'.format(
            self.basepath)

        with open(template) as f:
            documents = yaml.safe_load_all(f.read())
        valid, details = validate.validate_armada_documents(list(documents))

        self.assertTrue(valid)

    def test_validate_manifest_passes(self):
        manifest = yaml.safe_load(template_manifest)
        is_valid, error = validate.validate_armada_document(manifest)

        self.assertTrue(is_valid)

    def test_validate_chart_group_with_values(self):
        test_chart_group = """
---
schema: armada/ChartGroup/v1
metadata:
    name: kubernetes-proxy
    schema: metadata/Document/v1
data:
    description: Kubernetes proxy
    name: kubernetes-proxy
    sequenced: true
    chart_group:
      - proxy
---
schema: armada/Chart/v1
metadata:
    name: proxy
    schema: metadata/Document/v1
data:
    chart_name: proxy
    timeout: 600
    release: kubernetes-proxy
    source:
      subpath: proxy
      type: local
      location: "/etc/genesis/armada/assets/charts"
    namespace: kube-system
    upgrade:
      no_hooks: true
    values:
      images:
        tags:
          proxy: gcr.io/google_containers/hyperkube-amd64:v1.8.6
      network:
        kubernetes_netloc: 127.0.0.1:6553
    dependencies:
      - helm-toolkit
---
schema: armada/Chart/v1
metadata:
    name: helm-toolkit
    schema: metadata/Document/v1
data:
    chart_name: helm-toolkit
    wait:
      timeout: 600
    release: helm-toolkit
    source:
      reference: master
      subpath: helm-toolkit
      location: https://git.openstack.org/openstack/openstack-helm
      type: git
    namespace: helm-toolkit
    upgrade:
      no_hooks: true
    values: {}
    dependencies: []
"""

        chart_group = yaml.safe_load_all(test_chart_group)
        is_valid, error = validate.validate_armada_documents(list(chart_group))

        self.assertTrue(is_valid)

    def test_validate_group_passes(self):
        chart_group = yaml.safe_load(template_chart_group)
        is_valid, error = validate.validate_armada_document(chart_group)

        self.assertTrue(is_valid)

    def test_validate_chart_passes(self):
        chart = yaml.safe_load(template_chart)
        is_valid, error = validate.validate_armada_document(chart)

        self.assertTrue(is_valid)

    @testtools.skipUnless(
        base.is_connected(),
        'validate_manifest_url requires network connectivity.')
    def test_validate_manifest_url(self):
        value = 'url'
        self.assertFalse(validate.validate_manifest_url(value))
        value = 'https://raw.githubusercontent.com/att-comdev/' \
                'armada/master/examples/simple.yaml'
        self.assertTrue(validate.validate_manifest_url(value))

    def test_validate_manifest_filepath(self):
        value = 'filepath'
        self.assertFalse(validate.validate_manifest_filepath(value))
        value = '{}/resources/valid_armada_document.yaml'.format(
            self.basepath)
        self.assertTrue(validate.validate_manifest_filepath(value))


class ValidateNegativeTestCase(BaseValidateTest):

    def test_validate_load_duplicate_schemas_expect_runtime_error(self):
        """Validate that calling ``validate._load_schemas`` results in a
        ``RuntimeError`` being thrown, because the call is made during module
        import, and importing the schemas again in manually results in
        duplicates.
        """
        with self.assertRaisesRegexp(
                RuntimeError,
                'Duplicate schema specified for: .*'):
            validate._load_schemas()

    def test_validate_no_dictionary_expect_type_error(self):
        expected_error = 'The provided input "invalid" must be a dictionary.'
        self.assertRaisesRegexp(TypeError, expected_error,
                                validate.validate_armada_documents,
                                ['invalid'])

    def test_validate_invalid_chart_armada_manifest(self):
        template = '{}/resources/valid_armada_document.yaml'.format(
            self.basepath)

        with open(template) as f:
            documents = list(yaml.safe_load_all(f.read()))

        mariadb_document = [
            d for d in documents if d['metadata']['name'] == 'mariadb'][0]
        del mariadb_document['data']['release']

        _, error_messages = validate.validate_armada_documents(documents)
        expected_error = self._build_error_message(
            'armada/Chart/v1', 'mariadb',
            "'release' is a required property")

        self.assertEqual(1, len(error_messages))
        self.assertEqual(expected_error, error_messages[0]['message'])

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
        self.assertEqual(error[0]['message'], expected_error)

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
        self.assertEqual(error[0]['message'], expected_error)

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
        self.assertEqual(error[0]['message'], expected_error)
