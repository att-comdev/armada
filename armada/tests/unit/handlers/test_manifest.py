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

    def test_get_manifest(self):
        armada_manifest = manifest.Manifest(self.documents)
        obtained_manifest = armada_manifest.get_manifest()
        self.assertIsInstance(obtained_manifest, dict)
        self.assertEqual(obtained_manifest['armada'],
                         armada_manifest.manifest['data'])

    def test_find_documents(self):
        armada_manifest = manifest.Manifest(self.documents)
        chart_documents, chart_groups, manifests = armada_manifest. \
            _find_documents()

        # checking if all the chart documents are present
        self.assertIsInstance(chart_documents, list)

        helm_toolkit_chart = armada_manifest. \
            find_chart_document('helm-toolkit')
        self.assertEqual(chart_documents[0], helm_toolkit_chart)

        mariadb_chart = armada_manifest.find_chart_document('mariadb')
        self.assertEqual(chart_documents[1], mariadb_chart)

        memcached_chart = armada_manifest.find_chart_document('memcached')
        self.assertEqual(chart_documents[2], memcached_chart)

        keystone_chart = armada_manifest.find_chart_document('keystone')
        self.assertEqual(chart_documents[3], keystone_chart)

        # checking if all the chart group documents are present
        self.assertIsInstance(chart_groups, list)

        keystone_infra_services_chart_group = armada_manifest. \
            find_chart_group_document('keystone-infra-services')
        self.assertEqual(chart_groups[0],
                         keystone_infra_services_chart_group)

        openstack_keystone_chart_group = armada_manifest. \
            find_chart_group_document('openstack-keystone')
        self.assertEqual(chart_groups[1], openstack_keystone_chart_group)

        # verifying the manifests
        self.assertIsInstance(manifests, list)

        self.assertEqual(manifests[0], armada_manifest.manifest)

    def test_verify_chart_documents(self):
        armada_manifest = manifest.Manifest(self.documents)
        helm_toolkit_chart = armada_manifest. \
            find_chart_document('helm-toolkit')
        self.assertIsInstance(helm_toolkit_chart, dict)
        self.assertEqual(self.documents[0], helm_toolkit_chart)

        mariadb_chart = armada_manifest.find_chart_document('mariadb')
        self.assertIsInstance(mariadb_chart, dict)
        self.assertEqual(self.documents[1], mariadb_chart)

        memcached_chart = armada_manifest.find_chart_document('memcached')
        self.assertIsInstance(memcached_chart, dict)
        self.assertEqual(self.documents[2], memcached_chart)

        keystone_chart = armada_manifest.find_chart_document('keystone')
        self.assertIsInstance(keystone_chart, dict)
        self.assertEqual(self.documents[3], keystone_chart)

    def test_verify_chart_group_documents(self):
        armada_manifest = manifest.Manifest(self.documents)
        ok_chart = armada_manifest. \
            find_chart_group_document('openstack-keystone')
        self.assertIsInstance(ok_chart, dict)
        self.assertEqual(self.documents[-2], ok_chart)

        armada_manifest = manifest.Manifest(self.documents)
        kis_chart = armada_manifest.find_chart_group_document(
            'keystone-infra-services')
        self.assertIsInstance(kis_chart, dict)
        self.assertEqual(self.documents[-3], kis_chart)

    def test_verify_build_armada_manifest(self):
        armada_manifest = manifest.Manifest(self.documents)

        built_armada_manifest = armada_manifest.build_armada_manifest()

        self.assertIsNotNone(built_armada_manifest)
        self.assertIsInstance(built_armada_manifest, dict)

        # the first chart group in the armada manifest
        keystone_infra_services_chart_group = armada_manifest. \
            find_chart_group_document('keystone-infra-services')
        keystone_infra_services_chart_group_data = \
            keystone_infra_services_chart_group.get('data')

        self.assertEqual(keystone_infra_services_chart_group_data,
                         built_armada_manifest['data']['chart_groups'][0])

        # the first chart group in the armada manifest
        openstack_keystone_chart_group = armada_manifest. \
            find_chart_group_document('openstack-keystone')
        openstack_keystone_chart_group_data = \
            openstack_keystone_chart_group.get('data')

        self.assertEqual(openstack_keystone_chart_group_data,
                         built_armada_manifest['data']['chart_groups'][1])

    def test_verify_build_chart_group_deps(self):
        armada_manifest = manifest.Manifest(self.documents)
        # building the deps for openstack-keystone chart group
        chart_group = armada_manifest.find_chart_group_document(
            'openstack-keystone')
        openstack_keystone_chart_group_deps = armada_manifest. \
            build_chart_group(chart_group)
        openstack_keystone_chart_group_deps_dep_added = \
            openstack_keystone_chart_group_deps[
                'data']['chart_group'][0]['chart']['dependencies']

        # keystone chart dependencies
        keystone_chart = armada_manifest.find_chart_document('keystone')
        keystone_chart_with_deps = armada_manifest.build_chart_deps(
            keystone_chart)
        keystone_dependencies = keystone_chart_with_deps[
            'data']['dependencies']

        self.assertEqual(openstack_keystone_chart_group_deps_dep_added[0],
                         keystone_dependencies[0])

        # building the deps for openstack-keystone chart group
        chart_group = armada_manifest.find_chart_group_document(
            'keystone-infra-services')
        openstack_keystone_chart_group_deps = armada_manifest. \
            build_chart_group(chart_group)
        keystone_infra_services_dep_added = \
            openstack_keystone_chart_group_deps[
                'data']['chart_group'][0]['chart']['dependencies']

        # building mariadb chart dependencies
        mariadb_chart = armada_manifest.find_chart_document('mariadb')
        mariadb_chart_with_deps = armada_manifest.build_chart_deps(
            mariadb_chart)
        mariadb_dependencies = mariadb_chart_with_deps[
            'data']['dependencies']

        # building memcached chart dependencies
        memcached_chart = armada_manifest.find_chart_document('memcached')
        memcached_chart_with_deps = armada_manifest.build_chart_deps(
            memcached_chart)
        memcached_dependencies = memcached_chart_with_deps[
            'data']['dependencies']

        self.assertEqual(keystone_infra_services_dep_added[0],
                         mariadb_dependencies[0])
        self.assertEqual(keystone_infra_services_dep_added[0],
                         memcached_dependencies[0])

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

    def test_build_chart_deps_with_missing_dependency_fails(self):
        """Validate that attempting to build a chart that points to
        a missing dependency fails.
        """
        armada_manifest = manifest.Manifest(self.documents)
        self.documents[1]['data']['dependencies'] = ['missing-dependency']
        test_chart = armada_manifest.find_chart_document('mariadb')
        self.assertRaises(exceptions.ManifestException,
                          armada_manifest.build_chart_deps,
                          test_chart)

    def test_build_chart_group_with_missing_chart_grp_fails(self):
        """Validate that attempting to build a chart group document with
        missing chart group fails.
        """
        armada_manifest = manifest.Manifest(self.documents)
        self.documents[5]['data']['chart_group'] = ['missing-chart-group']
        test_chart_group = armada_manifest.find_chart_group_document(
            'openstack-keystone')
        self.assertRaises(exceptions.ManifestException,
                          armada_manifest.build_chart_group,
                          test_chart_group)

    def test_build_armada_manifest_with_missing_chart_grps_fails(self):
        """Validate that attempting to build a manifest with missing
        chart groups fails.
        """
        armada_manifest = manifest.Manifest(self.documents)
        self.documents[6]['data']['chart_groups'] = ['missing-manifest']
        self.assertRaises(exceptions.ManifestException,
                          armada_manifest.build_armada_manifest)
