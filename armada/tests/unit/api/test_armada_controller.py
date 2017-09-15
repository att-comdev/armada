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

import yaml

import mock
from oslo_config import cfg

from armada.handlers import armada
from armada.tests.unit.api import base

CONF = cfg.CONF


class ArmadaControllerTest(base.BaseControllerTest):

    @mock.patch.object(armada, 'validate')
    @mock.patch.object(armada, 'Manifest')
    @mock.patch.object(armada, 'Tiller')
    def test_armada_apply_resource(self, mock_tiller, mock_manifest,
                                   mock_validate):
        """Tests the POST /api/v1.0/apply endpoint."""
        rules = {'armada:create_endpoints': '@'}
        self.policy.set_rules(rules)

        manifest_file = """
        schema: armada/Manifest/v1
        metadata:
            schema: metadata/Document/v1
            name: example-manifest
        data:
            release_prefix: example
            chart_groups:
                - example-group
        """
        manifest_obj = yaml.load(manifest_file)

        mock_validate.validate_armada_documents.return_value = []
        mock_validate.validate_armada_object.return_value = True, None

        options = {'debug': 'true',
                   'disable_update_pre': 'false',
                   'disable_update_post': 'false',
                   'enable_chart_cleanup': 'false',
                   'skip_pre_flight': 'false',
                   'dry_run': 'false',
                   'wait': 'false',
                   'timeout': '100'}
        expected = {'message': {'diff': [], 'install': [], 'upgrade': []}}

        result = self.app.simulate_post(
            path='/api/v1.0/apply', body=manifest_file, params=options)
        self.assertEqual(expected, result.json)
        self.assertEqual('application/json', result.headers['content-type'])

        mock_tiller.assert_called_once_with(tiller_host=None,
                                            tiller_port=44134)
        mock_manifest.assert_called_with([manifest_obj])
        mock_validate.validate_armada_documents.assert_called_once_with(
            [manifest_obj])
        fake_manifest = mock_manifest.return_value.get_manifest.return_value
        mock_validate.validate_armada_object.assert_called_once_with(
            fake_manifest)
