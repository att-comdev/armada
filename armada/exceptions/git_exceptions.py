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

class GitException(base_exception.ArmadaBaseException):
    '''Base class for Git exceptions and error handling.'''

    message = 'An unknown error occured while cloning a Git repository.'

class GitLocationException(GitException):
    '''Exception that occurs when an error occurs cloning a Git repository.'''

    def __init__(self, location):
        self._location = location
        self._message = self._location + ' is not a valid git repository.'

        super(GitLocationException, self).__init__(self._message)

class SourceCleanupException(GitException):
    '''Exception that occurs for an invalid dir.'''

    def __init__(self, target_dir):
        self._target_dir = target_dir
        self._message = self._target_dir + ' is not a valid directory.'

        super(SourceCleanupException, self).__init__(self._message)
