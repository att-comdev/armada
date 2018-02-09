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


class LintException(base_exception.ArmadaBaseException):
    '''Base class for linting exceptions and errors.'''

    message = 'An unknown linting error occurred.'


class InvalidManifestException(LintException):
    '''
    Exception for invalid manifests.

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'Armada manifest invalid.'


class InvalidChartNameException(LintException):
    '''Exception that occurs when an invalid filename is encountered.'''

    message = 'Chart name must be a string.'


class InvalidChartDefinitionException(LintException):
    '''Exception when invalid chart definition is encountered.'''

    message = 'Invalid chart definition. Chart definition must be array.'


class InvalidReleaseException(LintException):
    '''Exception that occurs when a release is invalid.'''

    message = 'Release needs to be a string.'


class InvalidArmadaObjectException(LintException):
    '''
    Exception that occurs when an Armada object is not declared.

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'An Armada object was not declared.'
