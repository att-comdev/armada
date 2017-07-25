import pygit2
import requests
import tarfile
import tempfile
import shutil
from os import path

from ..exceptions import source_exceptions


def git_clone(repo_url, branch='master'):
    '''
    clones repo to a /tmp/ dir
    '''

    if repo_url == '':
        raise source_exceptions.GitLocationException(repo_url)

    _tmp_dir = tempfile.mkdtemp(prefix='armada', dir='/tmp')

    try:
        pygit2.clone_repository(repo_url, _tmp_dir, checkout_branch=branch)
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
        tarball_filename = tempfile.mkstemp(prefix='armada', dir='/tmp')[1]
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

    _tmp_dir = tempfile.mkdtemp(prefix='armada', dir='/tmp')

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
