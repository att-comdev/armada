# Copyright 2017 The Armada Authors.
#
# Licensed under the Apache License, Version 2.0 (the 'License'));
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_config import cfg

from keystoneauth1 import loading

from armada.conf import utils

default_options = [

    cfg.ListOpt(
        'armada_apply_roles',
        default=['admin'],
        help=utils.fmt('IDs of approved API access roles.')),

    cfg.StrOpt(
        'auth_url',
        default='http://0.0.0.0/v3',
        help=utils.fmt('The default Keystone authentication url.')),

    cfg.StrOpt(
        'certs',
        default=None,
        help=utils.fmt("""
Absolute path to the certificate file to use for chart registries
""")),

    cfg.StrOpt(
        'kubernetes_config_path',
        default='/home/user/.kube/',
        help=utils.fmt('Path to Kubernetes configurations.')),

    cfg.BoolOpt(
        'middleware',
        default='true',
        help=utils.fmt("""
Enables or disables Keystone authentication middleware.
""")),

    cfg.StrOpt(
        'project_domain_name',
        default='default',
        help=utils.fmt("""
The Keystone project domain name used for authentication.
""")),

    cfg.StrOpt(
        'project_name',
        default='admin',
        help=utils.fmt('The Keystone project name used for authentication.')),

    cfg.StrOpt(
        'ssh_key_path',
        default='/home/user/.ssh/',
        help=utils.fmt('Path to SSH private key.')),

    cfg.StrOpt(
        'tiller_pod_labels',
        default='app=helm,name=tiller',
        help=utils.fmt('Labels for the tiller pod.')),

    cfg.ListOpt(
        'tiller_release_roles',
        default=['admin'],
        help=utils.fmt('IDs of approved API access roles.')),

    cfg.ListOpt(
        'tiller_status_roles',
        default=['admin'],
        help=utils.fmt('IDs of approved API access roles.'))
]


def register_opts(conf):
    conf.register_opts(default_options)
    conf.register_opts(
        loading.get_auth_plugin_conf_options('password'),
        group='keystone_authtoken')


def list_opts():
    return {
        'DEFAULT': default_options,
        'keystone_authtoken': loading.get_auth_plugin_conf_options('password')}
