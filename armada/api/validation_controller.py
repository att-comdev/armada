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
from armada.utils.lint import validate_armada_documents

LOG = logging.getLogger(__name__)


class Validate(api.BaseResource):
    '''
    apply armada endpoint service
    '''

    @policy.enforce('armada:validate_manifest')
    def on_post(self, req, resp):
        try:
            manifest = self.req_yaml(req)
            documents = list(manifest)

            message = {
                'valid': validate_armada_documents(documents)
            }

            resp.status = falcon.HTTP_200
            resp.data = json.dumps(message)
            resp.content_type = 'application/json'

        except Exception:
            self.error(req.context, "Failed: Invalid Armada Manifest")
            self.return_error(
                resp,
                falcon.HTTP_400,
                message="Failed: Invalid Armada Manifest")
