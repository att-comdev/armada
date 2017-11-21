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
import socket
import shutil

import fixtures
import mock
import testtools

from armada.exceptions import source_exceptions
from armada.tests.unit import base
from armada.tests import test_utils
from armada.utils import source


def is_connected():
    """Verifies whether network connectivity is up.

    :returns: True if connected else False.
    """
    try:
        host = socket.gethostbyname("www.github.com")
        socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False


class GitTestCase(base.ArmadaTestCase):

    def _validate_git_clone(self, repo_dir, expected_ref=None):
        self.assertTrue(os.path.isdir(repo_dir))
        self.addCleanup(shutil.rmtree, repo_dir)
        self.assertIn('armada', repo_dir)
        # Assert that the directory is a Git repo.
        self.assertTrue(os.path.isdir(os.path.join(repo_dir, '.git')))
        if expected_ref:
            # Assert the FETCH_HEAD is at the expected ref.
            with open(os.path.join(repo_dir, '.git', 'FETCH_HEAD'), 'r') \
                    as git_file:
                self.assertIn(expected_ref, git_file.read())

    @testtools.skipUnless(
        is_connected(), 'git clone requires network connectivity.')
    def test_git_clone_good_url(self):
        url = 'http://github.com/att-comdev/armada'
        git_dir = source.git_clone(url)
        self._validate_git_clone(git_dir)

    @testtools.skipUnless(
        is_connected(), 'git clone requires network connectivity.')
    def test_git_clone_commit(self):
        url = 'http://github.com/att-comdev/armada'
        commit = 'cba78d1d03e4910f6ab1691bae633c5bddce893d'
        git_dir = source.git_clone(url, commit)
        self._validate_git_clone(git_dir)

    @testtools.skipUnless(
        is_connected(), 'git clone requires network connectivity.')
    def test_git_clone_ref(self):
        ref = 'refs/changes/54/457754/73'
        git_dir = source.git_clone(
            'https://github.com/openstack/openstack-helm', ref)
        self._validate_git_clone(git_dir, ref)

    @test_utils.attr(type=['negative'])
    @testtools.skipUnless(
        is_connected(), 'git clone requires network connectivity.')
    def test_git_clone_empty_url(self):
        url = ''
        # error_re = '%s is not a valid git repository.' % url

        self.assertRaises(source_exceptions.GitException,
                          source.git_clone, url)

    @test_utils.attr(type=['negative'])
    @testtools.skipUnless(
        is_connected(), 'git clone requires network connectivity.')
    def test_git_clone_bad_url(self):
        url = 'http://github.com/dummy/armada'

        self.assertRaises(source_exceptions.GitException,
                          source.git_clone, url)

    # TODO need to design a positive proxy test,
    #      difficult to achieve behind a corporate proxy
    @test_utils.attr(type=['negative'])
    @testtools.skipUnless(
        is_connected(), 'git clone requires network connectivity.')
    def test_git_clone_fake_proxy(self):
        url = 'http://github.com/att-comdev/armada'
        proxy_url = (test_utils.rand_name(
            prefix='http://', 'not.a.proxy.that.works.and.never.will')
            + ':8080')

        self.assertRaises(
            source_exceptions.GitProxyException,
            source.git_clone, url,
            proxy_server=proxy_url)

    @mock.patch('armada.utils.source.tempfile')
    @mock.patch('armada.utils.source.requests')
    def test_tarball_download(self, mock_requests, mock_temp):
        url = 'http://localhost:8879/charts/mariadb-0.1.0.tgz'
        mock_temp.mkstemp.return_value = (None, '/tmp/armada')
        mock_response = mock.Mock()
        mock_response.content = 'some string'
        mock_requests.get.return_value = mock_response

        mock_open = mock.mock_open()
        with mock.patch.object(source, 'open', mock_open, create=True):
            source.download_tarball(url)

        mock_temp.mkstemp.assert_called_once()
        mock_requests.get.assert_called_once_with(url, verify=False)
        mock_open.assert_called_once_with('/tmp/armada', 'wb')
        mock_open().write.assert_called_once_with(
            mock_requests.get(url).content)

    @mock.patch('armada.utils.source.tempfile')
    @mock.patch('armada.utils.source.os.path')
    @mock.patch('armada.utils.source.tarfile')
    def test_tarball_extract(self, mock_tarfile, mock_path, mock_temp):
        mock_path.exists.return_value = True
        mock_temp.mkdtemp.return_value = '/tmp/armada'
        mock_opened_file = mock.Mock()
        mock_tarfile.open.return_value = mock_opened_file

        path = '/tmp/mariadb-0.1.0.tgz'
        source.extract_tarball(path)

        mock_path.exists.assert_called_once()
        mock_temp.mkdtemp.assert_called_once()
        mock_tarfile.open.assert_called_once_with(path)
        mock_opened_file.extractall.assert_called_once_with('/tmp/armada')

    @test_utils.attr(type=['negative'])
    @mock.patch('armada.utils.source.os.path')
    @mock.patch('armada.utils.source.tarfile')
    def test_tarball_extract_bad_path(self, mock_tarfile, mock_path):
        mock_path.exists.return_value = False
        path = '/tmp/armada'

        self.assertRaises(source_exceptions.InvalidPathException,
                          source.extract_tarball, path)

        mock_tarfile.open.assert_not_called()
        mock_tarfile.extractall.assert_not_called()

    @testtools.skipUnless(
        is_connected(), 'git clone requires network connectivity.')
    @mock.patch.object(source, 'LOG')
    def test_source_cleanup(self, mock_log):
        url = 'http://github.com/att-comdev/armada'
        git_path = source.git_clone(url)
        source.source_cleanup(git_path)
        mock_log.warning.assert_not_called()

    @test_utils.attr(type=['negative'])
    @mock.patch.object(source, 'LOG')
    @mock.patch('armada.utils.source.shutil')
    def test_source_cleanup_fake_git_path(self, mock_shutil, mock_log):
        # Verify that passing in a fake path does nothing but log a warning.
        # Don't want anyone using the function to delete random directories.
        fake_path = self.useFixture(fixtures.TempDir()).path
        self.addCleanup(shutil.rmtree, fake_path)
        source.source_cleanup(fake_path)

        mock_shutil.rmtree.assert_not_called()
        self.assertTrue(mock_log.warning.called)
        actual_call = mock_log.warning.mock_calls[0][1][:2]
        self.assertEqual(
            ('%s is not a valid git repository. Details: %s', fake_path),
            actual_call)

    @test_utils.attr(type=['negative'])
    @mock.patch.object(source, 'LOG')
    @mock.patch('armada.utils.source.shutil')
    @mock.patch('armada.utils.source.os.path')
    def test_source_cleanup_missing_git_path(self, mock_path, mock_shutil,
                                             mock_log):
        # Verify that passing in a missing path does nothing but log a warning.
        mock_path.exists.return_value = False
        path = 'armada'
        source.source_cleanup(path)

        mock_shutil.rmtree.assert_not_called()
        self.assertTrue(mock_log.warning.called)
        actual_call = mock_log.warning.mock_calls[0][1]
        self.assertEqual(
            ('Could not delete the path %s. Is it a git repository?', path),
            actual_call)

    @test_utils.attr(type=['negative'])
    @mock.patch.object(source, 'os')
    def test_git_clone_ssh_auth_method_fails_auth(self, mock_os):
        mock_os.path.exists.return_value = True
        url = 'ssh://fmontei@fail.gerrithub.io:29418/att-comdev/armada'
        self.assertRaises(
            source_exceptions.GitAuthException, source.git_clone, url,
            ref='refs/changes/17/388517/5', auth_method='SSH')

    @test_utils.attr(type=['negative'])
    @mock.patch.object(source, 'os')
    def test_git_clone_ssh_auth_method_missing_ssh_key(self, mock_os):
        mock_os.path.exists.return_value = False
        url = 'ssh://fmontei@fail.gerrithub.io:29418/att-comdev/armada'
        self.assertRaises(
            source_exceptions.GitSSHException, source.git_clone, url,
            ref='refs/changes/17/388517/5', auth_method='SSH')
