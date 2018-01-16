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
from os import path

from git import Git
from git import Repo
from oslo_log import log as logging
import requests
from requests.packages import urllib3

from armada.exceptions import source_exceptions

LOG = logging.getLogger(__name__)


def git_clone(repo_url, ref='master'):
    '''Clone a git repository from ``repo_url`` using the reference ``ref``.

    :params repo_url: URL of git repo to clone.
    :params ref: branch, commit or reference in the repo to clone.
    :returns: Path to the cloned repo.
    '''

    if repo_url == '':
        raise source_exceptions.GitLocationException(repo_url)

    os.environ['GIT_TERMINAL_PROMPT'] = '0'
    _tmp_dir = tempfile.mkdtemp(prefix='armada')

    try:
        repo = Repo.clone_from(repo_url, _tmp_dir)
        repo.remotes.origin.fetch(ref)
        g = Git(repo.working_dir)
        g.checkout('FETCH_HEAD')
    except Exception:
        raise source_exceptions.GitLocationException(repo_url)

    return _tmp_dir


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
    if not path.exists(tarball_path):
        raise source_exceptions.InvalidPathException(tarball_path)

    _tmp_dir = tempfile.mkdtemp(prefix='armada')

    try:
        file = tarfile.open(tarball_path)
        file.extractall(_tmp_dir)
    except Exception:
        raise source_exceptions.TarballExtractException(tarball_path)
    return _tmp_dir


def source_cleanup(target_dir):
    '''Clean up the git repository that was created by ``git_clone`` above.

    Removes the ``target_dir`` repository and all associated files if they
    exist.

    :param str target_dir: The git repository to delete.
    '''
    if path.exists(target_dir):
        shutil.rmtree(target_dir)
    else:
        LOG.warning('Could not delete the path %s. Is it a git repository?',
                    target_dir)
