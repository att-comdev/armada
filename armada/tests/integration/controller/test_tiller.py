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


class TestTillerApi():

    def clean_up(self):
        tiller = Tiller()
        for iter in range(2):
            tiller.uninstall_release('armada-blog-{}'.format(iter + 1))

    def test_get_tiller_status(self, mocker, client):
        """
        Tiller status: /api/v1.0/status
        """

        mocked_policy = mocker.patch('armada.common.policy.enforce_policy')
        mocked_tiller = mocker.patch('armada.handlers.tiller')

        mocked_policy.return_value = True
        mocked_tiller._get_tiller_pod.return_value = '0.0.0.0'
        mocked_tiller.tiller_version.return_value = 'v2.7.0'

        doc = {
            'tiller': {
                'state': True,
                'version': 'v2.7.0'
            }
        }

        result = client.simulate_get('/api/v1.0/status')
        assert result.json == doc

    def test_get_tiller_release(self, mocker, client):
        """
        Tiller status: /api/v1.0/releases
        """

        mocked_policy = mocker.patch('armada.common.policy.enforce_policy')
        mocked_policy.return_value = True

        doc = {'releases': {}}

        result = client.simulate_get('/api/v1.0/releases')
        assert result.json == doc

        basepath = os.path.join(os.path.dirname(__file__))
        valid_manifest = '{}/templates/valid.yaml'.format(basepath)

        with open(valid_manifest) as f:
            file = f.read()
            client.simulate_post('/api/v1.0/apply', body=file)

        result = client.simulate_get('/api/v1.0/releases')

        doc = {'releases': {'default': ['armada-blog-2', 'armada-blog-1']}}

        assert result.json == doc

        self.clean_up()
