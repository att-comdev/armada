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

from armada.common.policies import base as policy_base
from armada.handlers import armada
from armada.tests import test_utils
from armada.tests.unit.api import base

CONF = cfg.CONF


class ArmadaControllerTest(base.BaseControllerTest):

    @mock.patch.object(armada, 'lint')
    @mock.patch.object(armada, 'Manifest')
    @mock.patch.object(armada, 'Tiller')
    def test_armada_apply_resource(self, mock_tiller, mock_manifest,
                                   mock_lint):
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
        payload = {'file': '', 'options': options}
        body = json.dumps(payload)
        expected = {'message': {'diff': [], 'install': [], 'upgrade': []}}

        result = self.app.simulate_post(path='/api/v1.0/apply', body=body)
        self.assertEqual(result.json, expected)
        self.assertEqual('application/json', result.headers['content-type'])

        mock_tiller.assert_called_once_with(tiller_host=None,
                                            tiller_port=44134)
        mock_manifest.assert_called_once_with([payload])
        mock_lint.validate_armada_documents.assert_called_once_with([payload])
        fake_manifest = mock_manifest.return_value.get_manifest.return_value
        mock_lint.validate_armada_object.assert_called_once_with(fake_manifest)


class ArmadaControllerNegativeRbacTest(base.BaseControllerTest):

    @test_utils.attr(type=['negative'])
    def test_armada_apply_resource_insufficient_permissions(self):
        """Tests the POST /api/v1.0/apply endpoint returns 403 following failed
        authorization.
        """
        rules = {'armada:create_endpoints': policy_base.RULE_ADMIN_REQUIRED}
        self.policy.set_rules(rules)
        resp = self.app.simulate_post('/api/v1.0/apply')
        self.assertEqual(403, resp.status_code)
