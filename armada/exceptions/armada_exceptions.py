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

from armada.exceptions import base_exception


class ArmadaException(base_exception.ArmadaBaseException):
    '''Base class for Armada handler exception and error handling.'''

    message = 'An unknown Armada handler error occurred.'


class ArmadaChartGroupTimeoutException(ArmadaException):
    '''Exception that occurs when Armada times out while processing.'''

    def __init__(self, chartgroup_name, chartgroup_desc):
        self._message = 'Armada timed out on ChartGroup: %s (%s).' % (
            chartgroup_name, chartgroup_desc)
        super(ArmadaChartGroupTimeoutException, self).__init__(self._message)


class KnownReleasesException(ArmadaException):
    '''
    Exception that occurs when no known releases are found.

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'No known releases found'
