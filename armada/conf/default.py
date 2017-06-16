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

from oslo_config import cfg

default_options = [
    cfg.StrOpt(
        'ssh_key_path',
        default='/home/user/.ssh/',
        help='Path to SSH private key.'),

    cfg.StrOpt(
        'logs',
        default='/var/log/armada/armada.log',
        help='Path to Armada logs.'),

    cfg.StrOpt(
        'kubernetes_config_path',
        default='/home/user/.kube/',
        help='Path to Kubernetes configurations.')
]

def register_opts(conf):
    conf.register_opts(default_options)

def list_opts():
    return {'DEFAULT': default_options}
