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

import copy
import os
import yaml

import testtools

from armada import const
from armada import exceptions
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

    def test_get_documents_with_target_manifest(self):
        # Validate that specifying `target_manifest` flag returns the correct
        # manifest.
        armada_manifest = manifest.Manifest(
            self.documents, target_manifest='armada-manifest')

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
        self.assertEqual('armada-manifest',
                         self.documents[-1]['metadata']['name'])

    def test_get_documents_with_multi_manifest_and_target_manifest(self):
        # Validate that specifying `target_manifest` flag returns the correct
        # manifest even if there are multiple existing manifests. (Only works
        # when the manifest names are distinct or else should raise error.)
        documents = copy.deepcopy(self.documents)
        other_manifest = copy.deepcopy(self.documents[-1])
        other_manifest['metadata']['name'] = 'alt-armada-manifest'
        documents.append(other_manifest)

        # Specify the "original" manifest and verify it works.
        armada_manifest = manifest.Manifest(
            documents, target_manifest='armada-manifest')

        self.assertIsInstance(armada_manifest.charts, list)
        self.assertIsInstance(armada_manifest.groups, list)
        self.assertIsNotNone(armada_manifest.manifest)

        self.assertEqual(4, len(armada_manifest.charts))
        self.assertEqual(2, len(armada_manifest.groups))

        self.assertEqual([self.documents[x] for x in range(4)],
                         armada_manifest.charts)
        self.assertEqual([self.documents[x] for x in range(4, 6)],
                         armada_manifest.groups)
        self.assertEqual(armada_manifest.manifest, self.documents[-1])
        self.assertEqual('armada-manifest',
                         armada_manifest.manifest['metadata']['name'])

        # Specify the alternative manifest and verify it works.
        armada_manifest = manifest.Manifest(
            documents, target_manifest='alt-armada-manifest')
        self.assertIsNotNone(armada_manifest.manifest)
        self.assertEqual(other_manifest, armada_manifest.manifest)
        self.assertEqual('alt-armada-manifest',
                         armada_manifest.manifest['metadata']['name'])

    def test_verify_chart_documents(self):
        armada_manifest = manifest.Manifest(self.documents)
        chart = armada_manifest.find_chart_document('helm-toolkit')
        self.assertEqual(self.documents[0], chart)

        chart = armada_manifest.find_chart_document('mariadb')
        self.assertEqual(self.documents[1], chart)

        chart = armada_manifest.find_chart_document('memcached')
        self.assertEqual(self.documents[2], chart)

        chart = armada_manifest.find_chart_document('keystone')
        self.assertEqual(self.documents[3], chart)

    def test_verify_chart_group_documents(self):
        armada_manifest = manifest.Manifest(self.documents)
        chart = armada_manifest.find_chart_group_document('openstack-keystone')
        self.assertEqual(self.documents[-2], chart)

        armada_manifest = manifest.Manifest(self.documents)
        chart = armada_manifest.find_chart_group_document(
            'keystone-infra-services')
        self.assertEqual(self.documents[-3], chart)

    def test_verify_build_chart_deps(self):
        armada_manifest = manifest.Manifest(self.documents)

        # helm-toolkit chart
        helm_toolkit_chart = armada_manifest.find_chart_document(
            'helm-toolkit')
        helm_toolkit_original_dependency = helm_toolkit_chart.get('data')
        helm_toolkit_chart_with_deps = armada_manifest.build_chart_deps(
            helm_toolkit_chart).get('data')

        # since not dependent on other charts, the original and modified
        # dependencies are the same
        self.assertEqual(helm_toolkit_original_dependency,
                         helm_toolkit_chart_with_deps)

        # helm-toolkit dependency, the basis for comparison of d
        # ependencies in other charts
        expected_helm_toolkit_dependency = {'chart': helm_toolkit_chart.get(
            'data')}

        # keystone chart dependencies
        keystone_chart = armada_manifest.find_chart_document('keystone')
        original_keystone_chart = copy.deepcopy(keystone_chart)
        keystone_chart_with_deps = armada_manifest.build_chart_deps(
            keystone_chart)

        self.assertNotEqual(original_keystone_chart, keystone_chart_with_deps)
        self.assertIn('data', keystone_chart_with_deps)
        self.assertIn('dependencies', keystone_chart_with_deps['data'])

        keystone_dependencies = keystone_chart_with_deps[
            'data']['dependencies']
        self.assertIsInstance(keystone_dependencies, list)
        self.assertEqual(1, len(keystone_dependencies))

        self.assertEqual(expected_helm_toolkit_dependency,
                         keystone_dependencies[0])

        # mariadb chart dependencies
        mariadb_chart = armada_manifest.find_chart_document('mariadb')
        original_mariadb_chart = copy.deepcopy(mariadb_chart)
        mariadb_chart_with_deps = armada_manifest.build_chart_deps(
            mariadb_chart)

        self.assertNotEqual(original_mariadb_chart, mariadb_chart_with_deps)
        self.assertIn('data', mariadb_chart_with_deps)
        self.assertIn('dependencies', mariadb_chart_with_deps['data'])

        mariadb_dependencies = mariadb_chart_with_deps[
            'data']['dependencies']
        self.assertIsInstance(mariadb_dependencies, list)
        self.assertEqual(1, len(mariadb_dependencies))

        self.assertEqual(expected_helm_toolkit_dependency,
                         mariadb_dependencies[0])

        # memcached chart dependencies
        memcached_chart = armada_manifest.find_chart_document('memcached')
        original_memcached_chart = copy.deepcopy(memcached_chart)
        memcached_chart_with_deps = armada_manifest.build_chart_deps(
            memcached_chart)

        self.assertNotEqual(original_memcached_chart,
                            memcached_chart_with_deps)
        self.assertIn('data', memcached_chart_with_deps)
        self.assertIn('dependencies', memcached_chart_with_deps['data'])

        memcached_dependencies = memcached_chart_with_deps[
            'data']['dependencies']
        self.assertIsInstance(memcached_dependencies, list)
        self.assertEqual(1, len(memcached_dependencies))

        self.assertEqual(expected_helm_toolkit_dependency,
                         memcached_dependencies[0])


class ManifestNegativeTestCase(testtools.TestCase):

    def setUp(self):
        super(ManifestNegativeTestCase, self).setUp()
        examples_dir = os.path.join(
            os.getcwd(), 'armada', 'tests', 'unit', 'resources')
        with open(os.path.join(examples_dir, 'keystone-manifest.yaml')) as f:
            self.documents = list(yaml.safe_load_all(f.read()))

    def test_get_documents_multi_manifests_raises_value_error(self):
        # Validates that finding multiple manifests without `target_manifest`
        # flag raises exceptions.ManifestException.
        documents = copy.deepcopy(self.documents)
        documents.append(documents[-1])  # Copy the last manifest.

        error_re = r'Multiple manifests are not supported.*'
        self.assertRaisesRegexp(
            exceptions.ManifestException, error_re, manifest.Manifest,
            documents)

    def test_get_documents_multi_target_manifests_raises_value_error(self):
        # Validates that finding multiple manifests with `target_manifest`
        # flag raises exceptions.ManifestException.
        documents = copy.deepcopy(self.documents)
        documents.append(documents[-1])  # Copy the last manifest.

        error_re = r'Multiple manifests are not supported.*'
        self.assertRaisesRegexp(
            exceptions.ManifestException, error_re, manifest.Manifest,
            documents, target_manifest='armada-manifest')

    def test_get_documents_missing_manifest(self):
        # Validates exceptions.ManifestException is thrown if no manifest is
        # found. Manifest is last document in sample YAML.
        error_re = ('Documents must be a list of documents with at least one '
                    'of each of the following schemas: .*')
        self.assertRaisesRegexp(
            exceptions.ManifestException, error_re, manifest.Manifest,
            self.documents[:-1])

    def test_get_documents_missing_charts(self):
        # Validates exceptions.ManifestException is thrown if no chart is
        # found. Charts are first 4 documents in sample YAML.
        error_re = ('Documents must be a list of documents with at least one '
                    'of each of the following schemas: .*')
        self.assertRaisesRegexp(
            exceptions.ManifestException, error_re, manifest.Manifest,
            self.documents[4:])

    def test_get_documents_missing_chart_groups(self):
        # Validates exceptions.ManifestException is thrown if no chart is
        # found. ChartGroups are 5-6 documents in sample YAML.
        documents = self.documents[:4] + [self.documents[-1]]
        error_re = ('Documents must be a list of documents with at least one '
                    'of each of the following schemas: .*')
        self.assertRaisesRegexp(
            exceptions.ManifestException, error_re, manifest.Manifest,
            documents)

    def test_find_chart_document_negative(self):
        armada_manifest = manifest.Manifest(self.documents)
        error_re = r'Could not find a %s named "%s"' % (
            const.DOCUMENT_CHART, 'invalid')
        self.assertRaisesRegexp(exceptions.ManifestException, error_re,
                                armada_manifest.find_chart_document, 'invalid')

    def test_find_group_document_negative(self):
        armada_manifest = manifest.Manifest(self.documents)
        error_re = r'Could not find a %s named "%s"' % (
            const.DOCUMENT_GROUP, 'invalid')
        self.assertRaisesRegexp(exceptions.ManifestException, error_re,
                                armada_manifest.find_chart_group_document,
                                'invalid')
