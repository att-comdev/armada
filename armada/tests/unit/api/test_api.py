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
from falcon import testing

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
        Test /api/v1.0/apply endpoint
        '''
        mock_armada.sync.return_value = None

        body = json.dumps({'file': '',
                           'options': {'debug': 'true',
                                       'disable_update_pre': 'false',
                                       'disable_update_post': 'false',
                                       'enable_chart_cleanup': 'false',
                                       'skip_pre_flight': 'false',
                                       'dry_run': 'false',
                                       'wait': 'false',
                                       'timeout': '100'}})

        doc = {u'message': u'Success'}

        result = self.simulate_post(path='/api/v1.0/apply', body=body)
        self.assertEqual(result.json, doc)

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
