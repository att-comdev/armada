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
from armada.utils.lint import validate_armada_documents
from armada.handlers.document import ReferenceResolver

class Validate(api.BaseResource):
    '''
    apply armada endpoint service
    '''

    @policy.enforce('armada:validate_manifest')
    def on_post(self, req, resp):
        try:
            if req.content_type == 'application/json':
                json_body = self.req_json(req)
                if 'href' in json_body:
                    ReferenceResolver.resolve_reference(json_body.get('href'))
                else:
                    resp.status = falcon.HTTP_400
                    return
            else:
                manifest = self.req_yaml(req)

            documents = list(manifest)

            result = validate_armada_documents(documents)

            resp.content_type = 'application/json'
            resp_body = {
                'kind': 'Status',
                'apiVersion': 'v1',
                'metadata': {},
                'reason': 'Validation',
                'details': {
                    'errorCount': 0,
                    'messageList': []
                },
            }

            if result:
                resp.status = falcon.HTTP_200
                resp_body['status'] = 'Valid'
                resp_body['message'] = 'Armada validations succeeded'
                resp_body['code'] = 200
            else:
                resp.status = falcon.HTTP_400
                resp_body['status'] = 'Invalid'
                resp_body['message'] = 'Armada validations failed'
                resp_body['code'] = 400
                resp_body['details']['errorCount'] = 1
                resp_body['details']['messageList'].append(dict(message='Validation failed.', error=True))

            resp.body = json.dumps(resp_body)
        except Exception:
            err_message = 'Failed to validate Armada Manifest'
            self.error(req.context, err_message)
            self.return_error(
                resp, falcon.HTTP_400, message=err_message)
