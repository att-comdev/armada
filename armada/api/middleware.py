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

import falcon

from keystoneauth1 import session
from keystoneauth1.identity import v3
from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class AuthMiddleware(object):

    def process_request(self, req, resp):

        # Validate token and get user session
        token = req.get_header('X-Auth-Token')
        req.context['session'] = self._get_user_session(token)

        # Add token roles to request context
        req.context['roles'] = self._get_roles(req.context['session'])

    def _get_roles(self, session):

        # Get roles IDs associated with user
        request_url = CONF.auth_url + '/role_assignments'
        resp = self._session_request(session=session, request_url=request_url)

        json_resp = resp.json()['role_assignments']
        role_ids = [r['role']['id'].encode('utf-8') for r in json_resp]

        # Get role names associated with role IDs
        roles = []
        for role_id in role_ids:
            request_url = CONF.auth_url + '/roles/' + role_id
            resp = self._session_request(session=session,
                                         request_url=request_url)

            role = resp.json()['role']['name'].encode('utf-8')
            roles.append(role)

        return roles

    def _get_user_session(self, token):

        # Get user session from token
        auth = v3.Token(auth_url=CONF.auth_url,
                        project_name=CONF.project_name,
                        project_domain_name=CONF.project_domain_name,
                        token=token)

        return session.Session(auth=auth)

    def _session_request(self, session, request_url):
        try:
            return session.get(request_url)
        except:
            raise falcon.HTTPUnauthorized('Authentication required',
                                          ('Authentication token is invalid.'))

class RoleMiddleware(object):

    def process_request(self, req, resp):
        endpoint = req.path
        roles = req.context['roles']

        # Verify roles have sufficient permissions for request endpoint
        if not (self._verify_roles(endpoint, roles)):
            raise falcon.HTTPUnauthorized('Insufficient permissions',
                                          ('Token role insufficient.'))

    def _verify_roles(self, endpoint, roles):

        # Compare the verified roles listed in the config with the user's
        # associated roles
        if endpoint == '/armada/apply':
            approved_roles = CONF.armada_apply_roles
        elif endpoint == '/tiller/releases':
            approved_roles = CONF.tiller_release_roles
        elif endpoint == '/tiller/status':
            approved_roles = CONF.tiller_status_roles

        verified_roles = set(roles).intersection(approved_roles)

        return bool(verified_roles)
