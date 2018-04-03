# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import yaml

import mock
import testtools

from armada.api.controller import test
from armada.common.policies import base as policy_base
from armada.exceptions import manifest_exceptions
from armada.tests import test_utils
from armada.tests.unit.api import base


class TestReleasesManifestControllerTest(base.BaseControllerTest):

    @mock.patch.object(test, 'Manifest')
    @mock.patch.object(test, 'Tiller')
    def test_test_controller_with_manifest(self, mock_tiller, mock_manifest):
        rules = {'armada:tests_manifest': '@'}
        self.policy.set_rules(rules)

        manifest_path = os.path.join(os.getcwd(), 'examples',
                                     'keystone-manifest.yaml')
        with open(manifest_path, 'r') as f:
            payload = f.read()
        documents = list(yaml.safe_load_all(payload))

        resp = self.app.simulate_post('/api/v1.0/tests', body=payload)
        self.assertEqual(200, resp.status_code)

        result = json.loads(resp.text)
        expected = {
            "tests": {"passed": [], "skipped": [], "failed": []}
        }
        self.assertEqual(expected, result)

        mock_manifest.assert_called_once_with(
            documents, target_manifest=None)
        self.assertTrue(mock_tiller.called)


class TestReleasesReleaseNameControllerTest(base.BaseControllerTest):

    @mock.patch.object(test, 'Tiller')
    def test_test_controller_test_pass(self, mock_tiller):
        rules = {'armada:test_release': '@'}
        self.policy.set_rules(rules)

        testing_release = mock_tiller.return_value.testing_release
        testing_release.return_value = mock.Mock(
            **{'info.status.last_test_suite_run.result': [
                mock.Mock(status='PASSED')]})

        resp = self.app.simulate_get('/api/v1.0/test/fake-release')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('MESSAGE: Test Pass',
                         json.loads(resp.text)['message'])

    @mock.patch.object(test, 'Tiller')
    def test_test_controller_test_fail(self, mock_tiller):
        rules = {'armada:test_release': '@'}
        self.policy.set_rules(rules)

        testing_release = mock_tiller.return_value.testing_release
        testing_release.return_value = mock.Mock(
            **{'info.status.last_test_suite_run.result': [
                mock.Mock(status='FAILED')]})

        resp = self.app.simulate_get('/api/v1.0/test/fake-release')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('MESSAGE: Test Fail',
                         json.loads(resp.text)['message'])

    @mock.patch.object(test, 'Tiller')
    def test_test_controller_no_test_found(self, mock_tiller):
        rules = {'armada:test_release': '@'}
        self.policy.set_rules(rules)

        mock_tiller.return_value.testing_release.return_value = None

        resp = self.app.simulate_get('/api/v1.0/test/fake-release')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('MESSAGE: No test found',
                         json.loads(resp.text)['message'])


@test_utils.attr(type=['negative'])
class TestReleasesManifestControllerNegativeTest(base.BaseControllerTest):

    @mock.patch.object(test, 'Manifest')
    @mock.patch.object(test, 'Tiller')
    def test_test_controller_tiller_exc_returns_500(self, mock_tiller, _):
        rules = {'armada:tests_manifest': '@'}
        self.policy.set_rules(rules)

        mock_tiller.side_effect = Exception

        resp = self.app.simulate_post('/api/v1.0/tests')
        self.assertEqual(500, resp.status_code)

    @testtools.skip('WIP')  # TODO(MarshM) unskip!
    @mock.patch.object(test, 'Manifest')
    @mock.patch.object(test, 'Tiller')
    def test_test_controller_validation_failure_returns_400(
            self, *_):
        rules = {'armada:tests_manifest': '@'}
        self.policy.set_rules(rules)

        manifest_path = os.path.join(os.getcwd(), 'examples',
                                     'keystone-manifest.yaml')
        with open(manifest_path, 'r') as f:
            payload = f.read()

        documents = list(yaml.safe_load_all(payload))
        documents[0]['schema'] = 'totally-invalid'
        invalid_payload = yaml.safe_dump_all(documents)

        resp = self.app.simulate_post('/api/v1.0/tests', body=invalid_payload)
        self.assertEqual(400, resp.status_code)

        resp_body = json.loads(resp.text)
        self.assertEqual(400, resp_body['code'])
        self.assertEqual(1, resp_body['details']['errorCount'])
        self.assertIn(
            {'message': (
                'An error occurred while generating the manifest: Could not '
                'find dependency chart helm-toolkit in armada/Chart/v1.'),
             'error': True,
             'kind': 'ValidationMessage',
             'level': 'Error',
             'name': 'ARM200',
             'documents': []},
            resp_body['details']['messageList'])
        self.assertEqual(('Failed to validate documents or generate Armada '
                          'Manifest from documents.'),
                         resp_body['message'])

    @mock.patch('armada.utils.validate.Manifest')
    @mock.patch.object(test, 'Tiller')
    def test_test_controller_manifest_failure_returns_400(
            self, _, mock_manifest):
        rules = {'armada:tests_manifest': '@'}
        self.policy.set_rules(rules)

        mock_manifest.return_value.get_manifest.side_effect = (
            manifest_exceptions.ManifestException(details='foo'))

        manifest_path = os.path.join(os.getcwd(), 'examples',
                                     'keystone-manifest.yaml')
        with open(manifest_path, 'r') as f:
            payload = f.read()

        resp = self.app.simulate_post('/api/v1.0/tests', body=payload)
        self.assertEqual(400, resp.status_code)

        resp_body = json.loads(resp.text)
        self.assertEqual(400, resp_body['code'])
        self.assertEqual(1, resp_body['details']['errorCount'])
        self.assertEqual(
            [{'message': (
                'An error occurred while generating the manifest: foo.'),
              'error': True,
              'kind': 'ValidationMessage',
              'level': 'Error',
              'name': 'ARM200',
              'documents': []}],
            resp_body['details']['messageList'])
        self.assertEqual(('Failed to validate documents or generate Armada '
                          'Manifest from documents.'),
                         resp_body['message'])


@test_utils.attr(type=['negative'])
class TestReleasesReleaseNameControllerNegativeTest(base.BaseControllerTest):

    @mock.patch.object(test, 'Tiller')
    def test_test_controller_tiller_exc_returns_500(self, mock_tiller):
        rules = {'armada:test_release': '@'}
        self.policy.set_rules(rules)

        mock_tiller.side_effect = Exception

        resp = self.app.simulate_get('/api/v1.0/test/fake-release')
        self.assertEqual(500, resp.status_code)


class TestReleasesReleaseNameControllerNegativeRbacTest(
        base.BaseControllerTest):

    @test_utils.attr(type=['negative'])
    def test_test_release_insufficient_permissions(self):
        """Tests the GET /api/v1.0/test/{release} endpoint returns 403
        following failed authorization.
        """
        rules = {'armada:test_release': policy_base.RULE_ADMIN_REQUIRED}
        self.policy.set_rules(rules)
        resp = self.app.simulate_get('/api/v1.0/test/test-release')
        self.assertEqual(403, resp.status_code)


class TestReleasesManifestControllerNegativeRbacTest(base.BaseControllerTest):

    @test_utils.attr(type=['negative'])
    def test_tests_manifest_insufficient_permissions(self):
        """Tests the POST /api/v1.0/tests endpoint returns 403 following failed
        authorization.
        """
        rules = {'armada:tests_manifest': policy_base.RULE_ADMIN_REQUIRED}
        self.policy.set_rules(rules)
        resp = self.app.simulate_post('/api/v1.0/tests')
        self.assertEqual(403, resp.status_code)
