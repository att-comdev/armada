# Copyright 2017 The Armada Authors.
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

import yaml

from oslo_config import cfg
from oslo_log import log as logging

from armada.exceptions import api_exceptions as err
from armada.handlers.armada import Override

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

API_VERSION = 'v{}/{}'


class ArmadaClient(object):

    def __init__(self, session):
        self.session = session

    def _set_endpoint(self, version, action):
        return API_VERSION.format(version, action)

    def get_status(self):

        endpoint = self._set_endpoint('1.0', 'status')
        resp = self.session.get(endpoint)

        self._check_response(resp)

        return resp.json()

    def get_releases(self):

        endpoint = self._set_endpoint('1.0', 'releases')
        resp = self.session.get(endpoint)

        self._check_response(resp)

        return resp.json()

    def post_validate(self, manifest=None):

        endpoint = self._set_endpoint('1.0', 'validate')
        resp = self.session.post(endpoint, body=manifest)

        self._check_response(resp)

        return resp.json()

    def post_apply(self, manifest=None, values=None, set=None, query=None):

        if values or set:
            document = list(yaml.safe_load_all(manifest))
            override = Override(
                document, overrides=set, values=values).update_manifests()
            manifest = yaml.dump(override)

        endpoint = self._set_endpoint('1.0', 'apply')
        resp = self.session.post(endpoint, body=manifest, query=query)

        self._check_response(resp)

        return resp.json()

    def get_test_release(self, release=None):

        endpoint = self._set_endpoint('1.0', 'test/{}'.format(release))
        resp = self.session.get(endpoint)

        self._check_response(resp)

        return resp.json()

    def post_test_manifest(self, manifest=None):

        endpoint = self._set_endpoint('1.0', 'tests')
        resp = self.session.post(endpoint, body=manifest)

        self._check_response(resp)

        return resp.json()

    def _check_response(self, resp):
        if resp.status_code == 401:
            raise err.ClientUnauthorizedError(
                "Unauthorized access to %s, include valid token.".format(
                    resp.url))
        elif resp.status_code == 403:
            raise err.ClientForbiddenError(
                "Forbidden access to %s" % resp.url)
        elif not resp.ok:
            raise err.ClientError(
                "Error - received %d: %s" % (resp.status_code, resp.text),
                code=resp.status_code)
