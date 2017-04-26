import pygit2
import tempfile
import shutil

def git_clone(repo_url, branch='master'):
    '''
    clones repo to a /tmp/ dir
    '''
    _tmp_dir = tempfile.mkdtemp(prefix='armada', dir='/tmp')
    pygit2.clone_repository(repo_url, _tmp_dir, checkout_branch=branch)

    return _tmp_dir

def source_cleanup(target_dir):
    '''
    Clean up source
    '''
    shutil.rmtree(target_dir)
