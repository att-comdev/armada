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
import string
import sys

from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF
DOMAIN = "armada"

def set_console_formatter(**formatter_kwargs):
    formatter_kwargs.setdefault(
        'fmt', '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    formatter_kwargs.setdefault('datefmt', '%m-%d %H:%M')

    # Specify default log levels
    custom_log_level_defaults = [
        'root=INFO',
        'cliff=INFO',
        'stevedore=INFO',
        'iso8601=INFO'
        ]

    logging.set_defaults(
        default_log_levels=logging.get_default_log_levels() +
        custom_log_level_defaults)

    # Specify log file location
    log_dir = os.path.expanduser('~/.armada')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = str(log_dir + '/armada.log')

    #CONF.register_opt(cfg.StrOpt('log_file', default=log_file))

    # Setup logging configuration
    logging.register_options(CONF)
    logging.setup(CONF, DOMAIN)
