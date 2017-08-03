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

armada_options = [

    cfg.ListOpt(
        'tiller_release_roles',
        default=['admin'],
        help='IDs of approved API access roles.'),

    cfg.ListOpt(
        'tiller_status_roles',
        default=['admin'],
        help='IDs of approved API access roles.'),

    cfg.StrOpt(
        'ssh_key_path',
        default='~/.ssh/',
        help='Path to SSH private key.'),

    cfg.StrOpt(
        'kubernetes_config_path',
        default='~/.kube/',
        help='Path to Kubernetes configurations.'),
]


def register_opts():
    CONF = cfg.CONF
    CONF.register_opts(armada_options, group='armada')

    # Load config file if exists
    default_config_file = 'etc/armada/armada.conf'
    if (os.path.exists(default_config_file)):
        CONF(['--config-file', default_config_file])

def list_opts():
    return {'armada': armada_options}
