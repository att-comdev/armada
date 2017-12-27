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

import os

from oslo_config import cfg
from oslo_log import log

from armada.conf import default
from armada import const

CONF = cfg.CONF

CONFIG_FILES = ['api-paste.ini', 'armada.conf']


def _get_config_files(env=None):
    if env is None:
        env = os.environ
    dirname = env.get('OS_ARMADA_CONFIG_DIR', const.CONFIG_PATH).strip()
    config_files = [
        os.path.join(dirname, config_file) for config_file in CONFIG_FILES
    ]
    return config_files


def set_app_default_configs():
    config_files = _get_config_files()
    if all([os.path.exists(x) for x in config_files]):
        CONF([], project='armada', default_config_files=config_files)
    set_default_for_default_log_levels()
    default.register_opts(CONF)


def set_default_for_default_log_levels():
    """Set the default for the default_log_levels option for Armada.
    Armada uses some packages that other OpenStack services don't use that do
    logging. This will set the default_log_levels default level for those
    packages.
    This function needs to be called before CONF().
    """

    extra_log_level_defaults = [
        'kubernetes.client.rest=INFO'
    ]

    log.set_defaults(
        default_log_levels=log.get_default_log_levels() +
        extra_log_level_defaults)
