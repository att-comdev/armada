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


class SourceException(base_exception.ArmadaBaseException):
    '''Base class for Git exceptions and error handling.'''

    message = 'An unknown error occured while accessing a chart source'


class GitLocationException(SourceException):
    '''Exception that occurs when an error occurs cloning a Git repository.'''

    def __init__(self, location):
        self._location = location
        self._message = self._location + ' is not a valid git repository.'

        super(GitLocationException, self).__init__(self._message)


class SourceCleanupException(SourceException):
    '''Exception that occurs for an invalid dir.'''

    def __init__(self, target_dir):
        self._target_dir = target_dir
        self._message = self._target_dir + ' is not a valid directory.'

        super(SourceCleanupException, self).__init__(self._message)


class TarballDownloadException(SourceException):
    '''Exception that occurs when the tarball cannot be downloaded
        from the provided URL
    '''

    def __init__(self, tarball_url):
        self._tarball_url = tarball_url
        self._message = 'Unable to download from ' + self._tarball_url

        super(TarballDownloadException, self).__init__(self._message)


class TarballExtractException(SourceException):
    '''Exception that occurs when extracting the tarball fails'''

    def __init__(self, tarball_dir):
        self._tarball_dir = tarball_dir
        self._message = 'Unable to extract ' + self._tarball_dir

        super(TarballExtractException, self).__init__(self._message)


class InvalidPathException(SourceException):
    '''Exception that occurs when a nonexistant path is accessed'''

    def __init__(self, path):
        self._path = path
        self._message = 'Unable to access path ' + self._path

        super(InvalidPathException, self).__init__(self._message)


class ChartSourceException(SourceException):
    '''Exception for unknown chart source type.'''

    def __init__(self, chart_name, source_type):
        self._chart_name = chart_name
        self._source_type = source_type

        self._message = 'Unknown source type \"' + self._source_type + '\" for \
                        chart \"' + self._chart_name + '\"'

        super(ChartSourceException, self).__init__(self._message)
