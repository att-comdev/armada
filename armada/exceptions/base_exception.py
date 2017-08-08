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

LOG = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 3600
CONF = cfg.CONF



class ArmadaBaseException(Exception):
    '''Base class for Armada exception and error handling.'''

    def __init__(self, message=None):
        self.message = message or self.message
        super(ArmadaBaseException, self).__init__(self.message)
