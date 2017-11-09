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

import pytest


class TestValidateApi():
    @pytest.mark.skip(reason="testing release via api is currently testable")
    def test_test_release(self, mocker, client):
        """
        Apply : /api/v1.0/test/{}
        """

        endpoint = '/api/v1.0/test/{}'
        mocked_policy = mocker.patch('armada.common.policy.enforce_policy')
        mocked_policy.return_value = True
        result = client.simulate_get(endpoint)

        assert result.json.get('type') == 'error'

        release_endpoint = endpoint.format('armada-blog-1')
        result = client.simulate_get(release_endpoint)
        assert result.json is True

    @pytest.mark.skip(reason="testing manifest via api is currently testable")
    def test_test_manifest(self, mocker, client):
        """
        Apply : /api/v1.0/test/{}
        """

        endpoint = '/api/v1.0/test/{}'
        mocked_policy = mocker.patch('armada.common.policy.enforce_policy')
        mocked_policy.return_value = True
        basepath = os.path.join(os.path.dirname(__file__))

        valid_manifest = '{}/templates/valid.yaml'.format(basepath)

        with open(valid_manifest) as f:
            result = client.simulate_post(endpoint, body=f.read())
            assert result.json is True
