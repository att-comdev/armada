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
import yaml

import falcon

from armada import api
from armada.common import policy
from armada.handlers.armada import Armada
from armada.handlers.document import ReferenceResolver
from armada.handlers.override import Override


class Apply(api.BaseResource):
    '''
    apply armada endpoint service
    '''
    @policy.enforce('armada:create_endpoints')
    def on_post(self, req, resp):
        try:

            # Load data from request and get options
            if req.content_type == 'application/x-yaml':
                data = list(self.req_yaml(req))
                if type(data[0]) is list:
                    documents = list(data[0])
                else:
                    documents = data
            elif req.content_type == 'application/json':
                self.logger.debug("Applying manifest based on reference.")
                req_body = self.req_json(req)
                doc_ref = req_body.get('hrefs', None)

                if not doc_ref:
                    self.logger.info("Request did not contain 'hrefs'.")
                    resp.status = falcon.HTTP_400
                    return

                data = ReferenceResolver.resolve_reference(doc_ref)
                documents = list()
                for d in data:
                    documents.extend(list(yaml.safe_load_all(d.decode())))

                if req_body.get('overrides', None):
                    overrides = Override(documents,
                                         overrides=req_body.get('overrides'))
                    documents = overrides.update_manifests()
            else:
                self.error(req.context, "Unknown content-type %s"
                           % req.content_type)
                self.return_error(
                    resp,
                    falcon.HTTP_415,
                    message="Request must be in application/x-yaml"
                            "or application/json")

            opts = req.params

            # Encode filename
            armada = Armada(
                documents,
                disable_update_pre=req.get_param_as_bool(
                    'disable_update_pre'),
                disable_update_post=req.get_param_as_bool(
                    'disable_update_post'),
                enable_chart_cleanup=req.get_param_as_bool(
                    'enable_chart_cleanup'),
                dry_run=req.get_param_as_bool('dry_run'),
                wait=req.get_param_as_bool('wait'),
                timeout=int(opts.get('timeout', 3600)),
                tiller_host=opts.get('tiller_host', None),
                tiller_port=int(opts.get('tiller_port', 44134)),
            )

            msg = armada.sync()

            resp.body = json.dumps(
                {
                    'message': msg,
                }
            )

            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200
        except Exception as e:
            err_message = 'Failed to apply manifest: {}'.format(e)
            self.error(req.context, err_message)
            self.return_error(
                resp, falcon.HTTP_500, message=err_message)
