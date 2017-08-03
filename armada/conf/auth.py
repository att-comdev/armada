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

import os

from oslo_config import cfg

auth_options = [
    cfg.StrOpt(
        'auth_strategy',
        default='keystone',
        help='Client request Auth strategy'),
    cfg.StrOpt(
        'admin_token',
        default='password',
        help='Client request Auth strategy', secret=True),
    cfg.StrOpt(
        'project_name',
        default='admin',
        help='The Keystone project name used for authentication.'),
    cfg.StrOpt(
        'project_domain_name',
        default='default',
        help='The Keystone project domain name used for authentication.'),
    cfg.ListOpt(
        'armada_apply_roles',
        default=['admin'],
        help='IDs of approved API access roles.'),
    cfg.StrOpt(
        'auth_strategy',
        default='keystone', help='Client request authentication strategy'),
    cfg.StrOpt(
        'auth_url',
        default='http://0.0.0.0/v3',
        help='The default Keystone authentication url.')
]

def register_opts():
    CONF = cfg.CONF
    CONF.register_opts(auth_options, group='auth')

    # Load config file if exists
    default_config_file = 'etc/armada/armada.conf'
    if (os.path.exists(default_config_file)):
        CONF(['--config-file', default_config_file])

def list_opts():
    return {'auth': auth_options}
