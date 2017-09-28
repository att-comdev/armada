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

from os import path
import os
import requests
import shutil
import tarfile
import tempfile

from git import Repo
from git import Git

from ..exceptions import source_exceptions


def git_clone(repo_url, branch='master'):
    '''
    :params repo_url - URL of git repo to clone
    :params branch - branch of the repo to clone

    Returns a path to the cloned repo
    '''

    if repo_url == '':
        raise source_exceptions.GitLocationException(repo_url)

    os.environ['GIT_TERMINAL_PROMPT'] = '0'
    _tmp_dir = tempfile.mkdtemp(prefix='armada')

    try:
        repo = Repo.clone_from(repo_url, _tmp_dir, **{'branch': 'master'})
        g = Git(repo.working_dir)
        g.checkout(branch)
    except Exception:
        raise source_exceptions.GitLocationException(repo_url)

    return _tmp_dir


def get_tarball(tarball_url):
    tarball_path = download_tarball(tarball_url)
    return extract_tarball(tarball_path)


def download_tarball(tarball_url):
    '''
    Downloads a tarball to /tmp and returns the path
    '''
    try:
        tarball_filename = tempfile.mkstemp(prefix='armada')[1]
        response = requests.get(tarball_url)
        with open(tarball_filename, 'wb') as f:
            f.write(response.content)
    except Exception:
        raise source_exceptions.TarballDownloadException(tarball_url)
    return tarball_filename


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
    '''
    Clean up source
    '''
    if path.exists(target_dir):
        shutil.rmtree(target_dir)
