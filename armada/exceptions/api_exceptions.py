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

from armada.exceptions import base_exception as base


class ApiException(base.ArmadaBaseException):
    '''
    Base class for API exceptions and error handling.

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'An unknown API error occurred.'


class ApiBaseException(ApiException):
    '''Exception that occurs during chart cleanup.'''

    message = 'There was an error listing the Helm chart releases.'


class ApiJsonException(ApiException):
    '''Exception that occurs during chart cleanup.'''

    message = 'There was an error listing the Helm chart releases.'


class ClientUnauthorizedError(ApiException):
    '''
    Exception that occurs when the server returns a 401 Unauthorized error.

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'There was an error listing the Helm chart releases.'


class ClientForbiddenError(ApiException):
    '''
    Exception that occurs when the server returns a 403 Forbidden error.

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'There was an error listing the Helm chart releases.'


class ClientError(ApiException):
    '''
    Exception that occurs when the server returns a 500 Internal Server error.

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'There was an error listing the Helm chart releases.'
