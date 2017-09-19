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
from oslo_log import log as logging

from armada import api
from armada.common import policy
from armada.handlers.armada import Armada

LOG = logging.getLogger(__name__)


class Apply(api.BaseResource):
    '''
    apply armada endpoint service
    '''
    @policy.enforce('armada:create_endpoints')
    def on_post(self, req, resp):
        try:

            # Load data from request and get options
            data = list(self.req_yaml(req))

            if type(data[0]) is list:
                data = list(data[0])

            opts = {}

            # Encode filename
            armada = Armada(
                data,
                disable_update_pre=opts.get('disable_update_pre', False),
                disable_update_post=opts.get('disable_update_post', False),
                enable_chart_cleanup=opts.get('enable_chart_cleanup', False),
                dry_run=opts.get('dry_run', False),
                wait=opts.get('wait', False),
                timeout=opts.get('timeout', False),
                tiller_host=opts.get('tiller_host', None),
                tiller_port=opts.get('tiller_port', 44134),
            )

            msg = armada.sync()

            resp.data = json.dumps(
                {
                    'message': msg,
                }
            )

            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200
        except Exception as e:
            self.error(req.context, "Failed to apply manifest")
            self.return_error(
                resp, falcon.HTTP_500,
                message="DATA {} \n Messge {}".format(data, e))
