import pygit2
import tempfile
import shutil
import requests

HTTP_OK = 200

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


def check_available_repo(repo_url):
    try:
        resp = requests.get(repo_url.replace('git:', 'http:'))
        if resp.status_code == HTTP_OK:
            return True

        return False
    except Exception:
        return False
