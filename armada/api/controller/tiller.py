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

from armada import api
from armada.common import policy
from armada.handlers.tiller import Tiller


class Status(api.BaseResource):
    @policy.enforce('tiller:get_status')
    def on_get(self, req, resp):
        '''
        get tiller status
        '''
        try:
            opts = req.params
            tiller = Tiller(
                tiller_host=opts.get('tiller_host', None),
                tiller_port=opts.get('tiller_port', None),
                tiller_namespace=opts.get('tiller_namespace', None))

            message = {
                'tiller': {
                    'state': tiller.tiller_status(),
                    'version': tiller.tiller_version()
                }
            }

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(message)
            resp.content_type = 'application/json'

        except Exception as e:
            err_message = 'Failed to get Tiller Status: {}'.format(e)
            self.error(req.context, err_message)
            self.return_error(
                resp, falcon.HTTP_500, message=err_message)


class Release(api.BaseResource):
    @policy.enforce('tiller:get_release')
    def on_get(self, req, resp):
        '''
        get tiller releases
        '''
        try:
            # Get tiller releases
            opts = req.params
            tiller = Tiller(tiller_host=opts.get('tiller_host', None),
                            tiller_port=opts.get('tiller_port', None),
                            tiller_namespace=opts.get('tiller_namespace',
                                                      None))

            releases = {}
            for release in tiller.list_releases():
                if not releases.get(release.namespace, None):
                    releases[release.namespace] = []

                releases[release.namespace].append(release.name)

            resp.body = json.dumps({'releases': releases})
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200

        except Exception as e:
            err_message = 'Unable to find Tiller Releases: {}'.format(e)
            self.error(req.context, err_message)
            self.return_error(
                resp, falcon.HTTP_500, message=err_message)
