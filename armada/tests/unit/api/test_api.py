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

from falcon import testing
from oslo_config import fixture as config_fixture

from armada import conf as cfg
from armada.api import server

CONF = cfg.CONF


class APITestCase(testing.TestCase):
    def setUp(self):
        super(APITestCase, self).setUp()
        self.app = server.create(middleware=False)


class TestAPI(APITestCase):
    @unittest.skip('this is incorrectly tested')
    @mock.patch('armada.api.armada_controller.Handler')
    def test_armada_apply(self, mock_armada):
        '''
        Test /armada/apply endpoint
        '''
        mock_armada.sync.return_value = None

        body = json.dumps({'file': '../examples/openstack-helm.yaml',
                           'options': {'debug': 'true',
                                       'disable_update_pre': 'false',
                                       'disable_update_post': 'false',
                                       'enable_chart_cleanup': 'false',
                                       'skip_pre_flight': 'false',
                                       'dry_run': 'false',
                                       'wait': 'false',
                                       'timeout': '100'}})

        doc = {u'message': u'Success'}

        result = self.simulate_post(path='/armada/apply', body=body)
        self.assertEqual(result.json, doc)

    @mock.patch('armada.api.tiller_controller.tillerHandler')
    def test_tiller_status(self, mock_tiller):
        '''
        Test /tiller/status endpoint
        '''

        # Mock tiller status value
        mock_tiller.tiller_status.return_value = 'Active'

        doc = {u'message': u'Tiller Server is Active'}

        result = self.simulate_get('/tiller/status')
        self.assertEqual(result.json, doc)

    @mock.patch('armada.api.tiller_controller.tillerHandler')
    def test_tiller_releases(self, mock_tiller):
        '''
        Test /tiller/releases endpoint
        '''

        # Mock tiller status value
        mock_tiller.list_releases.return_value = None

        doc = {u'releases': {}}

        result = self.simulate_get('/tiller/releases')
        self.assertEqual(result.json, doc)
