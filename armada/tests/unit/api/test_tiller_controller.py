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

import mock

from oslo_config import cfg

from armada.api.controller import tiller as tiller_controller
from armada.tests.unit.api import base

CONF = cfg.CONF


class TillerControllerTest(base.BaseControllerTest):

    @mock.patch.object(tiller_controller, 'Tiller')
    def test_get_tiller_status(self, mock_tiller):
        """Tests GET /api/v1.0/status endpoint."""
        rules = {'tiller:get_status': '@'}
        self.policy.set_rules(rules)

        mock_tiller.return_value.tiller_status.return_value = 'fake_status'
        mock_tiller.return_value.tiller_version.return_value = 'fake_verson'

        result = self.app.simulate_get('/api/v1.0/status')
        expected = {
            'tiller': {'version': 'fake_verson', 'state': 'fake_status'}
        }

        self.assertEqual(expected, result.json)
        self.assertEqual('application/json', result.headers['content-type'])
        mock_tiller.assert_called_once_with(tiller_host=None, tiller_port=None)

    @mock.patch.object(tiller_controller, 'Tiller')
    def test_get_tiller_status_with_params(self, mock_tiller):
        """Tests GET /api/v1.0/status endpoint with query parameters."""
        rules = {'tiller:get_status': '@'}
        self.policy.set_rules(rules)

        mock_tiller.return_value.tiller_status.return_value = 'fake_status'
        mock_tiller.return_value.tiller_version.return_value = 'fake_verson'

        result = self.app.simulate_get('/api/v1.0/status',
                                       params_csv=False,
                                       params={'tiller_host': 'fake_host',
                                               'tiller_port': '98765'})
        expected = {
            'tiller': {'version': 'fake_verson', 'state': 'fake_status'}
        }

        self.assertEqual(expected, result.json)
        self.assertEqual('application/json', result.headers['content-type'])
        mock_tiller.assert_called_once_with(tiller_host='fake_host',
                                            tiller_port='98765')

    @mock.patch.object(tiller_controller, 'Tiller')
    def test_tiller_releases(self, mock_tiller):
        """Tests GET /api/v1.0/releases endpoint."""
        rules = {'tiller:get_release': '@'}
        self.policy.set_rules(rules)

        def _get_fake_release(name, namespace):
            fake_release = mock.Mock(namespace='%s_namespace' % namespace)
            fake_release.configure_mock(name=name)
            return fake_release

        mock_tiller.return_value.list_releases.return_value = [
            _get_fake_release('foo', 'bar'), _get_fake_release('baz', 'qux')
        ]

        result = self.app.simulate_get('/api/v1.0/releases')
        expected = {
            'releases': {'bar_namespace': ['foo'], 'qux_namespace': ['baz']}
        }

        self.assertEqual(expected, result.json)
        mock_tiller.assert_called_once_with(tiller_host=None, tiller_port=None)
        mock_tiller.return_value.list_releases.assert_called_once_with()

    @mock.patch.object(tiller_controller, 'Tiller')
    def test_tiller_releases_with_params(self, mock_tiller):
        """Tests GET /api/v1.0/releases endpoint with query parameters."""
        rules = {'tiller:get_release': '@'}
        self.policy.set_rules(rules)

        def _get_fake_release(name, namespace):
            fake_release = mock.Mock(namespace='%s_namespace' % namespace)
            fake_release.configure_mock(name=name)
            return fake_release

        mock_tiller.return_value.list_releases.return_value = [
            _get_fake_release('foo', 'bar'), _get_fake_release('baz', 'qux')
        ]

        result = self.app.simulate_get('/api/v1.0/releases',
                                       params_csv=False,
                                       params={'tiller_host': 'fake_host',
                                               'tiller_port': '98765'})
        expected = {
            'releases': {'bar_namespace': ['foo'], 'qux_namespace': ['baz']}
        }

        self.assertEqual(expected, result.json)
        mock_tiller.assert_called_once_with(tiller_host='fake_host',
                                            tiller_port='98765')
        mock_tiller.return_value.list_releases.assert_called_once_with()
