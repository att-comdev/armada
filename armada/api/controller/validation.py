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
from oslo_config import cfg

from armada import api
from armada.common import policy
from armada.handlers.armada import Armada
from armada.handlers.document import ReferenceResolver
from armada.utils.validate import validate_armada_documents

CONF = cfg.CONF


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

            result, details = validate_armada_documents(documents)

            resp.content_type = 'application/json'
            resp_body = {
                'kind': 'Status',
                'apiVersion': 'v1.0',
                'metadata': {},
                'reason': 'Validation',
                'details': {},
            }

            error_details = [m for m in details if m.get('error', False)]

            resp_body['details']['errorCount'] = len(error_details)
            resp_body['details']['messageList'] = details

            # If validation was successful, also run a Tiller dry-run
            if result:
                try:
                    self.logger.info('Beginning dry-run of Armada')
                    armada = Armada(
                        documents,
                        dry_run=True,
                        tiller_host=req.get_param('tiller_host'),
                        tiller_port=req.get_param_as_int(
                            'tiller_port') or CONF.tiller_port,
                        tiller_namespace=req.get_param(
                            'tiller_namespace', default=CONF.tiller_namespace)
                    )
                    msg = armada.sync()
                    self.logger.info('Dry-run complete: %s', msg)
                except Exception as e:
                    self.logger.error('Armada validation was unable to '
                                      'process dry-run: %s', str(e))
            # TODO(MarshM) how to pass dryrun to client.post_validate() ??

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

            resp.body = json.dumps(resp_body)
        except Exception as ex:
            err_message = 'Failed to validate Armada Manifest'
            self.logger.error(err_message, exc_info=ex)
            self.return_error(
                resp, falcon.HTTP_400, message=err_message)
