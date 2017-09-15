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
import mock

from oslo_config import cfg

from armada.api.controller import armada as armada_api
from armada.tests.unit.api import base

CONF = cfg.CONF


class ArmadaControllerTest(base.BaseControllerTest):

    @mock.patch.object(armada_api, 'Armada')
    @mock.patch.object(armada_api, 'ReferenceResolver')
    def test_armada_apply_resource(self, mock_resolver, mock_armada):
        """Tests the POST /api/v1.0/apply endpoint."""
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

        expected_armada_options = {
            'disable_update_pre': False,
            'disable_update_post': False,
            'enable_chart_cleanup': False,
            'dry_run': False,
            'wait': False,
            'timeout': 100,
            'tiller_host': None,
            'tiller_port': 44134,
            'tiller_namespace': 'kube-system',
            'target_manifest': None
        }

        payload_url = 'http://foo.com/test.yaml'
        payload = {'hrefs': [payload_url]}
        body = json.dumps(payload)
        expected = {'message': {'diff': [], 'install': [], 'upgrade': []}}

        mock_resolver.resolve_reference.return_value = \
            [b"---\nfoo: bar"]

        mock_armada.return_value.sync.return_value = \
            {'diff': [], 'install': [], 'upgrade': []}

        result = self.app.simulate_post(path='/api/v1.0/apply',
                                        body=body,
                                        headers={
                                            'Content-Type': 'application/json'
                                        },
                                        params=options)
        self.assertEqual(result.json, expected)
        self.assertEqual('application/json', result.headers['content-type'])

        mock_resolver.resolve_reference.assert_called_with([payload_url])
        mock_armada.assert_called_with([{'foo': 'bar'}],
                                       **expected_armada_options)
        mock_armada.return_value.sync.assert_called()

    def test_armada_apply_no_href(self):
        """Tests /api/v1.0/apply returns 400 when hrefs list is empty."""
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
        payload = {'hrefs': []}
        body = json.dumps(payload)

        result = self.app.simulate_post(path='/api/v1.0/apply',
                                        body=body,
                                        headers={
                                            'Content-Type': 'application/json'
                                        },
                                        params=options)
        self.assertEqual(result.status_code, 400)
