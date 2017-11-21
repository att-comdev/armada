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

from git import exc as git_exc
from git import Git
from git import Repo
from oslo_config import cfg
from oslo_log import log as logging
import requests
from requests.packages import urllib3

from armada.exceptions import source_exceptions

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def git_clone(repo_url, ref='master', proxy_server=None, auth_method=None):
    '''Clone a git repository from ``repo_url`` using the reference ``ref``.

    :param repo_url: URL of git repo to clone.
    :param ref: branch, commit or reference in the repo to clone. Default is
        'master'.
    :param proxy_server: optional, HTTP proxy to use while cloning the repo.
    :param auth_method: Method to use for authenticating against the repository
        specified in ``repo_url``.  If value is "SSH" Armada attempts to
        authenticate against the repository using the SSH key specified under
        ``CONF.ssh_key_path``. If value is None, authentication is skipped.
        Valid values include "SSH" or None. Note that the values are not
        case sensitive. Default is None.
    :returns: Path to the cloned repo.
    :raises GitException: If ``repo_url`` is invalid or could not be found.
    :raises GitAuthException: If authentication with the Git repository failed.
    :raises GitProxyException: If the repo could not be cloned due to a proxy
        issue.
    :raises GitSSHException: If the SSH key specified by ``CONF.ssh_key_path``
        could not be found and ``auth_method`` is "SSH".
    '''

    if not repo_url:
        raise source_exceptions.GitException(repo_url)

    env_vars = {'GIT_TERMINAL_PROMPT': '0'}
    temp_dir = tempfile.mkdtemp(prefix='armada')
    ssh_cmd = None

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
    else:
        LOG.debug('Attempting to clone the repo at %s using reference %s '
                  'with no authentication.', repo_url, ref)

    try:
        if proxy_server:
            LOG.debug('Cloning [%s] with proxy [%s]', repo_url, proxy_server)
            repo = Repo.clone_from(repo_url, temp_dir, env=env_vars,
                                   config='http.proxy=%s' % proxy_server)
        else:
            LOG.debug('Cloning [%s]', repo_url)
            repo = Repo.clone_from(repo_url, temp_dir, env=env_vars)

        repo.remotes.origin.fetch(ref)
        g = Git(repo.working_dir)
        g.checkout('FETCH_HEAD')
    except git_exc.GitCommandError as e:
        LOG.exception('Encountered GitCommandError during clone.')
        if ssh_cmd and ssh_cmd in e.stderr:
            raise source_exceptions.GitAuthException(repo_url,
                                                     CONF.ssh_key_path)
        elif 'Could not resolve proxy' in e.stderr:
            raise source_exceptions.GitProxyException(proxy_server)
        else:
            raise source_exceptions.GitException(repo_url)
    except Exception:
        LOG.exception('Encountered unknown Exception during clone.')
        raise source_exceptions.GitException(repo_url)

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
            Repo(git_path)
        except git_exc.InvalidGitRepositoryError as e:
            LOG.warning('%s is not a valid git repository. Details: %s',
                        git_path, e)
        else:
            shutil.rmtree(git_path)
    else:
        LOG.warning('Could not delete the path %s. Is it a git repository?',
                    git_path)
