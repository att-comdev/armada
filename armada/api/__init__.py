# Copyright 2017 The Armada Authors.  All other rights reserved.
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

import uuid
import json

from falcon import request
from falcon import HTTP_200, HTTP_403, HTTP_401
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class BaseResource(object):
    def __init__(self, policy_engine=None):

        if policy_engine is None:
            raise ValueError('API resources require a RBAC policy engine')
        else:
            self.policy = policy_engine

    def check_policy(self, action, ctx):
        return self.policy.authorize(action, ctx)

    def access_denied(self, req, resp, action):
        if req.context.authenticated:
            self.info(req.context,
                      "Error - Forbidden access - action: %s" % action)
            self.return_error(resp, HTTP_403, message="Forbidden", retry=False)
        else:
            self.info(req.context, "Error - Unauthenticated access")
            self.return_error(
                resp, HTTP_401, message="Unauthenticated", retry=False)

    def on_options(self, req, resp):
        self_attrs = dir(self)
        methods = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'PATCH']
        allowed_methods = []

        for m in methods:
            if 'on_' + m.lower() in self_attrs:
                allowed_methods.append(m)

        resp.headers['Allow'] = ','.join(allowed_methods)
        resp.status = HTTP_200

    def req_json(self, req):
        if req.content_length is None or req.content_length == 0:
            return None

        if req.content_type is not None and req.content_type.lower(
        ) == 'application/json':
            raw_body = req.stream.read(req.content_length or 0)

            if raw_body is None:
                return None

            try:
                json_body = raw_body
                return json_body
            except json.JSONDecodeError as jex:
                raise Exception("%s: Invalid JSON in body: %s" % (req.path,
                                                                  jex))
        else:
            raise Exception("Requires application/json payload")

    def return_error(self, resp, status_code, message="", retry=False):
        resp.body = json.dumps({
            'type': 'error',
            'message': message,
            'retry': retry
        })
        resp.status = status_code

    def log_error(self, ctx, level, msg):
        extra = {'user': 'N/A', 'req_id': 'N/A', 'external_ctx': 'N/A'}

        if ctx is not None:
            extra = {
                'user': ctx.user,
                'req_id': ctx.request_id,
                'external_ctx': ctx.external_marker,
            }

        LOG.log(level, msg, extra=extra)

    def debug(self, ctx, msg):
        self.log_error(ctx, logging.DEBUG, msg)

    def info(self, ctx, msg):
        self.log_error(ctx, logging.INFO, msg)

    def warn(self, ctx, msg):
        self.log_error(ctx, logging.WARN, msg)

    def error(self, ctx, msg):
        self.log_error(ctx, logging.ERROR, msg)


class ArmadaRequestContext(object):
    def __init__(self):
        self.log_level = 'ERROR'
        self.user = None  # Username
        self.user_id = None  # User ID (UUID)
        self.user_domain_id = None  # Domain owning user
        self.roles = ['anyone']
        self.project_id = None
        self.project_domain_id = None  # Domain owning project
        self.is_admin_project = False
        self.authenticated = False
        self.request_id = str(uuid.uuid4())
        self.external_marker = ''

    def set_log_level(self, level):
        if level in ['error', 'info', 'debug']:
            self.log_level = level

    def set_user(self, user):
        self.user = user

    def set_project(self, project):
        self.project = project

    def add_role(self, role):
        self.roles.append(role)

    def add_roles(self, roles):
        self.roles.extend(roles)

    def remove_role(self, role):
        self.roles = [x for x in self.roles if x != role]

    def set_external_marker(self, marker):
        self.external_marker = marker

    def to_policy_view(self):
        policy_dict = {}

        policy_dict['user_id'] = self.user_id
        policy_dict['user_domain_id'] = self.user_domain_id
        policy_dict['project_id'] = self.project_id
        policy_dict['project_domain_id'] = self.project_domain_id
        policy_dict['roles'] = self.roles
        policy_dict['is_admin_project'] = self.is_admin_project

        return policy_dict


class ArmadaRequest(request.Request):
    context_type = ArmadaRequestContext
