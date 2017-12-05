# Copyright 2017 The Armada Authors.
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
import mock
import unittest

import falcon
from oslo_config import cfg

from armada.handlers import armada
from armada.tests.unit.api import base

CONF = cfg.CONF


class ArmadaControllerTest(base.BaseControllerTest):

    @mock.patch.object(armada, 'lint')
    @mock.patch.object(armada, 'Manifest')
    @mock.patch.object(armada, 'Tiller')
    def test_armada_apply_resource(self, mock_tiller, mock_manifest,
                                   mock_lint):
        rules = {'armada:create_endpoints': '@'}
        self.policy.set_rules(rules)

        options = {'debug': 'true',
                   'disable_update_pre': 'false',
                   'disable_update_post': 'false',
                   'enable_chart_cleanup': 'false',
                   'skip_pre_flight': 'false',
                   'dry_run': 'false',
                   'wait': 'false',
                   'timeout': '100'}
        payload = {'file': '', 'options': options}
        body = json.dumps(payload)
        expected = {'message': {'diff': [], 'install': [], 'upgrade': []}}

        result = self.app.simulate_post(path='/api/v1.0/apply', body=body)
        self.assertEqual(result.json, expected)

        mock_tiller.assert_called_once_with(tiller_host=None,
                                            tiller_port=44134)
        mock_manifest.assert_called_once_with([payload])
        mock_lint.validate_armada_documents.assert_called_once_with([payload])
        fake_manifest = mock_manifest.return_value.get_manifest.return_value
        mock_lint.validate_armada_object.assert_called_once_with(fake_manifest)

    @unittest.skip('Test does not handle auth/policy correctly')
    @mock.patch('armada.api.tiller_controller.Tiller')
    def test_tiller_status(self, mock_tiller):
        '''
        Test /status endpoint
        Test /api/v1.0/status endpoint
        '''

        # Mock tiller status value
        mock_tiller.tiller_status.return_value = 'Active'

        # FIXME(lamt) This variable is unused.  Uncomment when it is.
        # doc = {u'message': u'Tiller Server is Active'}

        result = self.simulate_get('/api/v1.0/status')

        # TODO(lamt) This should be HTTP_401 if no auth is happening, but auth
        # is not implemented currently, so it falls back to a policy check
        # failure, thus a 403.  Change this once it is completed

        # Fails due to invalid access
        self.assertEqual(falcon.HTTP_403, result.status)

        # FIXME(lamt) Need authentication - mock, fixture
        # self.assertEqual(result.json, doc)

    @unittest.skip('Test does not handle auth/policy correctly')
    @mock.patch('armada.api.tiller_controller.Tiller')
    def test_tiller_releases(self, mock_tiller):
        '''
        Test /api/v1.0/releases endpoint
        '''

        # Mock tiller status value
        mock_tiller.list_releases.return_value = None

        # FIXME(lamt) This variable is unused. Uncomment when it is.
        # doc = {u'releases': {}}

        result = self.simulate_get('/api/v1.0/releases')

        # TODO(lamt) This should be HTTP_401 if no auth is happening, but auth
        # is not implemented currently, so it falls back to a policy check
        # failure, thus a 403.  Change this once it is completed
        self.assertEqual(falcon.HTTP_403, result.status)

        # FIXME(lamt) Need authentication - mock, fixture
        # self.assertEqual(result.json, doc)
