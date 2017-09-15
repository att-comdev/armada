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
from armada.utils.validate import validate_armada_documents


class Validate(api.BaseResource):
    """Controller for validating Armada manifests."""

    @policy.enforce('armada:validate_manifest')
    def on_post(self, req, resp):
        """Validates Armada's manifests.

        .. note::

            This action is a POST because Shipyard requires that it be when
            it performs its "validate design" action.
        """

        errors = []
        try:
            documents = list(self.req_yaml(req))
            valid, errors = validate_armada_documents(documents)
        except TypeError:
            err_message = {
                'reason': 'Failed to validate Armada manifest.',
                'errors': errors
            }
            self.error(req.context, err_message)
            self.return_error(
                resp, falcon.HTTP_400, message=err_message)
        except Exception:
            err_message = {
                'reason': 'Unknown validation error occurred.',
                'errors': errors
            }
            self.error(req.context, err_message)
            self.return_error(
                resp, falcon.HTTP_500, message=err_message)       
        else:
            resp_body = {
                'valid': valid,
                'errors': errors
            }
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(resp_body)
            resp.content_type = 'application/json'
