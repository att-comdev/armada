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
from oslo_log import log

from armada.conf import default
from armada import const

CONF = cfg.CONF

# Load oslo_log options prior to file/CLI parsing
log.register_options(CONF)

# Load config file if exists
if (os.path.exists(const.CONFIG_PATH)):
    CONF(['--config-file', const.CONFIG_PATH])


def set_app_default_configs():
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

    log.register_options(CONF)
    log.set_defaults(
        default_log_levels=log.get_default_log_levels() +
        extra_log_level_defaults)
