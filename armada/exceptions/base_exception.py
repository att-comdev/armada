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

import falcon
from oslo_config import cfg
from oslo_log import log as logging

from armada.common.i18n import _

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class ArmadaBaseException(Exception):
    '''Base class for Armada exception and error handling.'''

    def __init__(self, message=None, **kwargs):
        self.message = message or self.message
        try:  # nosec
            self.message = self.message % kwargs
        except Exception:
            pass
        super(ArmadaBaseException, self).__init__(self.message)


class ArmadaAPIException(falcon.HTTPError):
    '''Base class for Armada API Exceptions.'''

    status = falcon.HTTP_500
    message = "unknown error"
    title = "Internal Server Error"

    def __init__(self, message=None, **kwargs):
        self.message = message or self.message
        super(ArmadaAPIException, self).__init__(
            self.status, self.title, self.message, **kwargs
        )


class ActionForbidden(ArmadaAPIException):
    '''
    Exception thrown when an action is forbidden.

    **Troubleshoot:**
    *Coming Soon*
    '''

    status = falcon.HTTP_403
    message = _("Insufficient privilege to perform action.")
    title = _("Action Forbidden")
