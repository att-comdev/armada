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

from falcon import HTTP_200, HTTP_500
from oslo_config import cfg
from oslo_log import log as logging

from armada import api
from armada.handlers.armada import Armada


LOG = logging.getLogger(__name__)
CONF = cfg.CONF



class Apply(api.BaseResource):
    '''
    apply armada endpoint service
    '''

    def on_post(self, req, resp):

        try:
            policy_action = 'chart_installer:install'
            ctx = req.context

            if not self.check_policy(policy_action, ctx):
                self.access_denied(req, resp, policy_action)
                return

            data = self.req_json(req)
            # opts = data['options']
            opts = {}
            if data is not None:
                armada = Armada(
                    data,
                    disable_update_pre=opts.get('disable_update_pre', False),
                    disable_update_post=opts.get('disable_update_post', False),
                    enable_chart_cleanup=opts.get(
                        'enable_chart_cleanup', False),
                    dry_run=opts.get('dry_run', False),
                    wait=opts.get('wait', False),
                )

                armada.sync()

            resp.data = json.dumps({'success': True})
            resp.content_type = 'application/json'
            resp.status = HTTP_200

        except Exception:
            self.error(req.context, "Failed to apply manifest")
            self.return_error(
                resp,
                HTTP_500,
                message="Failed to apply manifest"
            )
