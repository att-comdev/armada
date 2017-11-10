# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
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
"""Utility functions for accessing Openstack Keystone."""

import os

from keystoneauth1.identity import v3
from keystoneauth1 import session
from oslo_config import cfg


CONF = cfg.CONF


class KeystoneUtils(object):
    """Utility methods for using Keystone."""

    @staticmethod
    def get_session():
        """Get an initialized keystone session.

        Authentication is based on the keystone_authtoken
        section of the config file primarily. If that fails
        then attempt to create a session from environmental
        variables. This is for cases of the CLI needing
        a token.
        """
        auth_info = dict()
        auth_fields = ['auth_url', 'username', 'password', 'project_id',
                       'user_domain_name']
        try:
            for f in auth_fields:
                auth_info[f] = getattr(CONF.keystone_authtoken, f)
            auth = v3.Password(**auth_info)
            ks_session = session.Session(auth=auth)
            # Test the session
            ks_session.get_auth_headers()
        except Exception:  # nosec this isn't a security issue
            pass
        else:
            return ks_session

        try:
            for f in auth_fields:
                auth_info[f] = os.environ.get('os_{}'.format(f).upper())
            auth = v3.Password(**auth_info)
            ks_session = session.Session(auth=auth)
            # Test the session
            ks_session.get_auth_headers()
        except Exception:
            raise Exception('Missing credential information for Keystone.')

        return ks_session
