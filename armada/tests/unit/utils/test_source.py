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

import mock
import unittest

from armada.exceptions import source_exceptions
from armada.utils import source


class GitTestCase(unittest.TestCase):

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

    def test_git_clone_good_url(self):
        url = 'http://github.com/att-comdev/armada'
        git_dir = source.git_clone(url)
        self._validate_git_clone(git_dir)

    def test_git_clone_commit(self):
        url = 'http://github.com/att-comdev/armada'
        commit = 'cba78d1d03e4910f6ab1691bae633c5bddce893d'
        git_dir = source.git_clone(url, commit)
        self._validate_git_clone(git_dir)

    def test_git_clone_ref(self):
        ref = 'refs/changes/54/457754/73'
        git_dir = source.git_clone(
            'https://github.com/openstack/openstack-helm', ref)
        self._validate_git_clone(git_dir, ref)

    def test_git_clone_empty_url(self):
        url = ''
        error_re = '%s is not a valid git repository.' % url

        with self.assertRaisesRegexp(
                source_exceptions.GitLocationException, error_re):
            source.git_clone(url)

    def test_git_clone_bad_url(self):
        url = 'http://github.com/dummy/armada'
        error_re = '%s is not a valid git repository.' % url

        with self.assertRaisesRegexp(
                source_exceptions.GitLocationException, error_re):
            source.git_clone(url)

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
    @mock.patch('armada.utils.source.path')
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

    @mock.patch('armada.utils.source.path')
    @mock.patch('armada.utils.source.tarfile')
    def test_tarball_extract_bad_path(self, mock_tarfile, mock_path):
        mock_path.exists.return_value = False
        path = '/tmp/armada'
        with self.assertRaises(source_exceptions.InvalidPathException):
            source.extract_tarball(path)

        mock_tarfile.open.assert_not_called()
        mock_tarfile.extractall.assert_not_called()

    @mock.patch('armada.utils.source.shutil')
    @mock.patch('armada.utils.source.path')
    def test_source_cleanup(self, mock_path, mock_shutil):
        mock_path.exists.return_value = True
        path = 'armada'

        try:
            source.source_cleanup(path)
        except source_exceptions.SourceCleanupException:
            pass

        mock_shutil.rmtree.assert_called_with(path)

    @unittest.skip('not handled correctly')
    @mock.patch('armada.utils.source.shutil')
    @mock.patch('armada.utils.source.path')
    def test_source_cleanup_bad_path(self, mock_path, mock_shutil):
        mock_path.exists.return_value = False
        path = 'armada'
        with self.assertRaises(source_exceptions.InvalidPathException):
            source.source_cleanup(path)
        mock_shutil.rmtree.assert_not_called()
