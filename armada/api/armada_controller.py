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
from armada.handlers.armada import Armada

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class Apply(api.BaseResource):
    '''
    apply armada endpoint service
    '''

    @policy.enforce('armada:create_endpoints')
    def on_post(self, req, resp):
        try:

            # Load data from request and get options
            data = json.load(req.stream)
            opts = data['options']

            # Encode filename
            data['file'] = data['file'].encode('utf-8')

            armada = Armada(open(data['file']),
                            disable_update_pre=opts['disable_update_pre'],
                            disable_update_post=opts['disable_update_post'],
                            enable_chart_cleanup=opts['enable_chart_cleanup'],
                            dry_run=opts['dry_run'],
                            wait=opts['wait'],
                            timeout=opts['timeout'])

            armada.sync()

            resp.data = json.dumps({'message': 'Success'})
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200
        except Exception:
            self.error(req.context, "Failed to apply manifest")
            self.return_error(
                resp,
                falcon.HTTP_500,
                message="Failed to apply manifest"
            )
