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

import base_exception

class OverrideException(base_exception.ArmadaBaseException):
    '''
    Base class for Override handler exception and error handling.
    '''

    message = 'An unknown Override handler error occured.'

class InvalidOverrideTypeException(OverrideException):
    '''
    Exception that occurs when an invalid override type is used with the
    set flag.
    '''

    def __init__(self, override_type):
        self._message = 'Override type "{}" is invalid'.format(override_type)

        super(InvalidOverrideTypeException, self).__init__(self._message)

class InvalidOverrideValueException(OverrideException):
    '''
    Exception that occurs when an invalid value is used with the set flag.
    '''

    def __init__(self, override_command):
        self._message = '{} is not a valid override statement.'.format(
                        override_command)

        super(InvalidOverrideValueException, self).__init__(self._message)
