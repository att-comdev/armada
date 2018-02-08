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

    message = 'An unknown error occurred while accessing a chart source.'


class GitException(SourceException):
    '''
    Exception when an error occurs cloning a Git repository.

    **Troubleshoot:**
    *Coming Soon*
    '''

    def __init__(self, location):
        self._location = location
        self._message = ('Git exception occurred, [', self._location,
                         '] may not be a valid git repository.')

        super(GitException, self).__init__(self._message)


class GitAuthException(SourceException):
    '''Exception that occurs when authentication fails for cloning a repo.'''

    def __init__(self, repo_url, ssh_key_path):
        self._repo_url = repo_url
        self._ssh_key_path = ssh_key_path

        self._message = ('Failed to authenticate for repo {} with ssh-key at '
                         'path {}. Verify the repo exists and the correct ssh '
                         'key path was supplied in the Armada config '
                         'file.').format(self._repo_url, self._ssh_key_path)

        super(GitAuthException, self).__init__(self._message)


class GitProxyException(SourceException):
    '''Exception when an error occurs cloning a Git repository
       through a proxy.'''

    def __init__(self, location):
        self._location = location
        self._message = ('Could not resolve proxy [', self._location, '].')

        super(GitProxyException, self).__init__(self._message)


class GitSSHException(SourceException):
    '''Exception that occurs when an SSH key could not be found.'''

    def __init__(self, ssh_key_path):
        self._ssh_key_path = ssh_key_path

        self._message = (
            'Failed to find specified SSH key: {}.'.format(self._ssh_key_path))

        super(GitSSHException, self).__init__(self._message)


class SourceCleanupException(SourceException):
    '''Exception that occurs for an invalid dir.'''

    def __init__(self, target_dir):
        self._target_dir = target_dir
        self._message = self._target_dir + ' is not a valid directory.'

        super(SourceCleanupException, self).__init__(self._message)


class TarballDownloadException(SourceException):
    '''
    Exception that occurs when the tarball cannot be downloaded from the
    provided URL.

    **Troubleshoot:**
    *Coming Soon*
    '''

    def __init__(self, tarball_url):
        self._tarball_url = tarball_url
        self._message = 'Unable to download from ' + self._tarball_url

        super(TarballDownloadException, self).__init__(self._message)


class TarballExtractException(SourceException):
    '''
    Exception that occurs when extracting the tarball fails.

    **Troubleshoot:**
    *Coming Soon*
    '''

    def __init__(self, tarball_dir):
        self._tarball_dir = tarball_dir
        self._message = 'Unable to extract ' + self._tarball_dir

        super(TarballExtractException, self).__init__(self._message)


class InvalidPathException(SourceException):
    '''
    Exception that occurs when a nonexistant path is accessed.

    **Troubleshoot:**
    *Coming Soon*
    '''

    def __init__(self, path):
        self._path = path
        self._message = 'Unable to access path ' + self._path

        super(InvalidPathException, self).__init__(self._message)


class ChartSourceException(SourceException):
    '''
    Exception for unknown chart source type.

    **Troubleshoot:**
    *Coming Soon*
    '''

    def __init__(self, chart_name, source_type):
        self._chart_name = chart_name
        self._source_type = source_type

        self._message = 'Unknown source type \"' + self._source_type + '\" for \
                        chart \"' + self._chart_name + '\"'

        super(ChartSourceException, self).__init__(self._message)
