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

import json

import falcon
from oslo_config import cfg
from oslo_log import log as logging

from armada import api
from armada.common import policy
from armada.handlers.tiller import Tiller

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class Status(api.BaseResource):

    @policy.enforce('tiller:get_status')
    def on_get(self, req, resp):
        '''
        get tiller status
        '''
        try:
            message = {
                'tiller': Tiller().tiller_status()
            }

            if message.get('tiller', False):
                resp.data = json.dumps(message)
                resp.status = falcon.HTTP_200
                LOG.info('Tiller Server %s', message.get('tiller', False))
            else:
                resp.data = json.dumps(message.get('tiller', False))
                resp.status = falcon.HTTP_503
                LOG.info('Tiller Server %s', message.get('tiller', False))

            resp.content_type = 'application/json'

        except Exception:
            self.error(req.context, "Unable to find resources")
            self.return_error(
                resp,
                falcon.HTTP_500,
                message="Unable to find resource"
            )


class Release(api.BaseResource):

    @policy.enforce('tiller:get_release')
    def on_get(self, req, resp):
        '''
        get tiller releases
        '''
        try:
            # Get tiller releases
            handler = Tiller()

            releases = {}
            for release in handler.list_releases():
                releases[release.name] = release.namespace

            resp.data = json.dumps({'releases': releases})
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200

        except Exception:
            self.error(req.context, "Unable to find resources")
            self.return_error(
                resp,
                falcon.HTTP_500,
                message="Unable to find Armada Release"
            )
