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
from oslo_log import log as logging

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class CliAction(object):

    def __init__(self):
        self.logger = LOG
        logging.register_options(CONF)
        logging.set_defaults(default_log_levels=CONF.default_log_levels)
        logging.setup(CONF, 'armada')

    def invoke(self):
        raise Exception()
