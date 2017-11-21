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

import os
import shutil
import tarfile
import tempfile

import git
from oslo_config import cfg
from oslo_log import log as logging
import requests
from requests.packages import urllib3

from armada.exceptions import source_exceptions

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def git_clone(repo_url, ref='master', auth_method=None):
    '''Clone a git repository from ``repo_url`` using the reference ``ref``.

    :param repo_url: URL of git repo to clone.
    :param ref: branch, commit or reference in the repo to clone. Default is
        'master' branch.
    :param auth_method: Method to use for authenticating against the repository
        specified in ``repo_url``.  If value is "SSH" Armada attempts to
        authenticate against the repository using the SSH key specified under
        ``CONF.ssh_key_path``. If value is None, authentication is skipped.
        Valid values include "SSH" or None. Note that the values are not
        case sensitive. Default is None.
    :returns: Path to the cloned repo.
    :raises GitLocationException: If ``repo_url`` is invalid or could not be
        found.
    :raises GitAuthException: If authentication with the Git repository failed.
    '''

    if not repo_url:
        raise source_exceptions.GitLocationException(repo_url)

    env_vars = {'GIT_TERMINAL_PROMPT': '0'}
    temp_dir = tempfile.mkdtemp(prefix='armada')

    try:
        if auth_method and auth_method.lower() == 'ssh':
            LOG.debug('Attempting to clone the repo at %s using reference %s '
                      'with SSH authentication.', repo_url, ref)

            if not os.path.exists(CONF.ssh_key_path):
                LOG.error('SSH auth method was specified for cloning repo but '
                          'the SSH key under CONF.ssh_key_path was not found.')
                raise source_exceptions.GitSSHException(CONF.ssh_key_path)

            ssh_cmd = (
                'ssh -i {} -o ConnectionAttempts=20 -o ConnectTimeout=10'
                .format(os.path.expanduser(CONF.ssh_key_path))
            )
            env_vars.update({'GIT_SSH_COMMAND': ssh_cmd})
            repo = git.Repo.clone_from(repo_url, temp_dir, env=env_vars)
        else:
            LOG.debug('Attempting to clone the repo at %s using reference %s '
                      'with no authentication.', repo_url, ref)
            repo = git.Repo.clone_from(repo_url, temp_dir, env=env_vars)

        repo.remotes.origin.fetch(ref)
        g = git.Git(repo.working_dir)
        g.checkout('FETCH_HEAD')
    except git.exc.GitCommandError as e:
        if 'ssh' in repo_url or '@' in repo_url:
            raise source_exceptions.GitAuthException(repo_url,
                                                     CONF.ssh_key_path)
        else:
            LOG.error('%s is not a valid git repository. Details: %s',
                      repo_url, e)
            raise source_exceptions.GitLocationException(repo_url)

    return temp_dir


def get_tarball(tarball_url, verify=False):
    tarball_path = download_tarball(tarball_url, verify=verify)
    return extract_tarball(tarball_path)


def download_tarball(tarball_url, verify=False):
    '''
    Downloads a tarball to /tmp and returns the path
    '''
    try:
        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        tarball_filename = tempfile.mkstemp(prefix='armada')[1]
        response = requests.get(tarball_url, verify=verify)

        with open(tarball_filename, 'wb') as f:
            f.write(response.content)

        return tarball_filename
    except Exception:
        raise source_exceptions.TarballDownloadException(tarball_url)


def extract_tarball(tarball_path):
    '''
    Extracts a tarball to /tmp and returns the path
    '''
    if not os.path.exists(tarball_path):
        raise source_exceptions.InvalidPathException(tarball_path)

    temp_dir = tempfile.mkdtemp(prefix='armada')

    try:
        file = tarfile.open(tarball_path)
        file.extractall(temp_dir)
    except Exception:
        raise source_exceptions.TarballExtractException(tarball_path)
    return temp_dir


def source_cleanup(git_path):
    '''Clean up the git repository that was created by ``git_clone`` above.

    Removes the ``git_path`` repository and all associated files if they
    exist.

    :param str git_path: The git repository to delete.
    '''
    if os.path.exists(git_path):
        try:
            # Internally validates whether the path points to an actual repo.
            git.Repo(git_path)
        except git.exc.InvalidGitRepositoryError as e:
            LOG.warning('%s is not a valid git repository. Details: %s',
                        git_path, e)
        else:
            shutil.rmtree(git_path)
    else:
        LOG.warning('Could not delete the path %s. Is it a git repository?',
                    git_path)
