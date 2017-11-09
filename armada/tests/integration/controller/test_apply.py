# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
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

import os

from armada.handlers.tiller import Tiller


class TestValidateApi():
    def clean_up(self):
        tiller = Tiller()
        for iter in range(2):
            tiller.uninstall_release('armada-blog-{}'.format(iter + 1))

    def test_validate_status(self, mocker, client):
        """
        Apply : /api/v1.0/apply
        """

        endpoint = '/api/v1.0/apply'
        mocked_policy = mocker.patch('armada.common.policy.enforce_policy')
        mocked_policy.return_value = True
        basepath = os.path.join(os.path.dirname(__file__))
        valid_manifest = '{}/templates/valid.yaml'.format(basepath)
        invalid_manifest = '{}/templates/invalid.yaml'.format(basepath)

        doc = {
            'message': {
                'diff': [],
                'install': [],
                'upgrade': [],
            }
        }

        install_doc = {
            'message': {
                'diff': [],
                'install': [],
                'upgrade': [],
            }
        }

        for iter in range(2):
            install_doc['message']['install'].append(
                'armada-blog-{}'.format(iter + 1))

        result = client.simulate_post(endpoint)

        assert result.json.get('type') == 'error'

        with open(valid_manifest) as f:
            file = f.read()
            result = client.simulate_post(endpoint, body=file)
            assert result.json == install_doc

            result = client.simulate_post(endpoint, body=file)
            self.clean_up()
            assert result.json == doc

        with open(invalid_manifest) as f:
            result = client.simulate_post(endpoint, body=f.read())
            assert result.json.get('type') == 'error'
