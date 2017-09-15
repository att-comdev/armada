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
import yaml

from armada import api
from armada.common import policy
from armada.utils.validate import validate_armada_documents
from armada.handlers.document import ReferenceResolver


class Validate(api.BaseResource):
    '''Controller for validating an Armada manifest.
    '''

    @policy.enforce('armada:validate_manifest')
    def on_post(self, req, resp):
        try:
            if req.content_type == 'application/json':
                self.logger.debug("Validating manifest based on reference.")
                json_body = self.req_json(req)
                if json_body.get('href', None):
                    self.logger.debug("Validating manifest from reference %s."
                                      % json_body.get('href'))
                    data = ReferenceResolver.resolve_reference(
                        json_body.get('href'))
                    documents = list()
                    for d in data:
                        documents.extend(list(yaml.safe_load_all(d.decode())))
                else:
                    resp.status = falcon.HTTP_400
                    return
            else:
                manifest = self.req_yaml(req)
                documents = list(manifest)

            self.logger.debug("Validating set of %d documents."
                              % len(documents))

            result = validate_armada_documents(documents)

            resp.content_type = 'application/json'
            resp_body = {
                'kind': 'Status',
                'apiVersion': 'v1.0',
                'metadata': {},
                'reason': 'Validation',
                'details': {
                    'errorCount': 0,
                    'messageList': []
                },
            }

            if result:
                resp.status = falcon.HTTP_200
                resp_body['status'] = 'Success'
                resp_body['message'] = 'Armada validations succeeded'
                resp_body['code'] = 200
            else:
                resp.status = falcon.HTTP_400
                resp_body['status'] = 'Failure'
                resp_body['message'] = 'Armada validations failed'
                resp_body['code'] = 400
                resp_body['details']['errorCount'] = 1
                resp_body['details']['messageList'].\
                    append(dict(message='Validation failed.', error=True))

            resp.body = json.dumps(resp_body)
        except Exception as ex:
            err_message = 'Failed to validate Armada Manifest'
            self.logger.error(err_message, exc_info=ex)
            self.return_error(
                resp, falcon.HTTP_400, message=err_message)
