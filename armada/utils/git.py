import pygit2
import tempfile
import shutil
from os import path


def git_clone(repo_url, branch='master'):
    '''
    clones repo to a /tmp/ dir
    '''

    if repo_url == '':
        return False

    _tmp_dir = tempfile.mkdtemp(prefix='armada', dir='/tmp')
    pygit2.clone_repository(repo_url, _tmp_dir, checkout_branch=branch)

    return _tmp_dir


def source_cleanup(target_dir):
    '''
    Clean up source
    '''
    if path.exists(target_dir):
        shutil.rmtree(target_dir)
