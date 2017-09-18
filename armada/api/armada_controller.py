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

from builtins import object
import json

import falcon
from oslo_log import log as logging

from armada import api
from armada.handlers.armada import Armada

LOG = logging.getLogger(__name__)

class Apply(api.BaseResource):
    '''
    apply armada endpoint service
    '''

    def on_post(self, req, resp):
        try:

            # Load data from request and get options
            data = self.req_json(req)
            opts = {}
            # opts = data['options']

            # Encode filename
            # data['file'] = data['file'].encode('utf-8')
            armada = Armada(
                data,
                disable_update_pre=opts.get('disable_update_pre', False),
                disable_update_post=opts.get('disable_update_post', False),
                enable_chart_cleanup=opts.get('enable_chart_cleanup', False),
                dry_run=opts.get('dry_run', False),
                wait=opts.get('wait', False),
                timeout=opts.get('timeout', False))

            msg = armada.sync()

            resp.data = json.dumps({'message': msg})

            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200
        except Exception as e:
            self.error(req.context, "Failed to apply manifest")
            self.return_error(
                resp, falcon.HTTP_500,
                message="Failed to install manifest: {} {}".format(e, data))
