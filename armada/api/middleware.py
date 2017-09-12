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

import re

from oslo_config import cfg
from oslo_log import log as logging

from armada.common import policy

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class AuthMiddleware(object):

    # Authentication
    def process_request(self, req, resp):
        ctx = req.context

        ctx.set_policy_engine(policy.policy_engine)

        for k, v in req.headers.items():
            LOG.debug("Request with header %s: %s" % (k, v))

        auth_status = req.get_header('X-SERVICE-IDENTITY-STATUS')
        service = True

        if auth_status is None:
            auth_status = req.get_header('X-IDENTITY-STATUS')
            service = False

        if auth_status == 'Confirmed':
            # Process account and roles
            ctx.authenticated = True
            ctx.user = req.get_header(
                'X-SERVICE-USER-NAME') if service else req.get_header(
                    'X-USER-NAME')
            ctx.user_id = req.get_header(
                'X-SERVICE-USER-ID') if service else req.get_header(
                    'X-USER-ID')
            ctx.user_domain_id = req.get_header(
                'X-SERVICE-USER-DOMAIN-ID') if service else req.get_header(
                    'X-USER-DOMAIN-ID')
            ctx.project_id = req.get_header(
                'X-SERVICE-PROJECT-ID') if service else req.get_header(
                    'X-PROJECT-ID')
            ctx.project_domain_id = req.get_header(
                'X-SERVICE-PROJECT-DOMAIN-ID') if service else req.get_header(
                    'X-PROJECT-DOMAIN-NAME')
            if service:
                ctx.add_roles(req.get_header('X-SERVICE-ROLES').split(','))
            else:
                ctx.add_roles(req.get_header('X-ROLES').split(','))

            if req.get_header('X-IS-ADMIN-PROJECT') == 'True':
                ctx.is_admin_project = True
            else:
                ctx.is_admin_project = False

            LOG.debug(
                'Request from authenticated user %s with roles %s' %
                (ctx.user, ','.join(ctx.roles)))
        else:
            ctx.authenticated = False


class ContextMiddleware(object):
    def __init__(self):
        # Setup validation pattern for external marker
        UUIDv4_pattern = '^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$'
        self.marker_re = re.compile(UUIDv4_pattern, re.I)

    def process_request(self, req, resp):
        ctx = req.context

        ext_marker = req.get_header('X-Context-Marker')

        if ext_marker is not None and self.marker_re.fullmatch(ext_marker):
            ctx.set_external_marker(ext_marker)


class LoggingMiddleware(object):

    def process_response(self, req, resp, resource, req_succeeded):
        ctx = req.context
        extra = {
            'user': ctx.user,
            'req_id': ctx.request_id,
            'external_ctx': ctx.external_marker,
        }
        resp.append_header('X-Drydock-Req', ctx.request_id)
        LOG.info("%s - %s" % (req.uri, resp.status), extra=extra)
