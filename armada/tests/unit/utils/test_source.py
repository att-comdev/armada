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

import mock
import unittest

from armada.exceptions import source_exceptions

from armada.utils import source

class GitTestCase(unittest.TestCase):

    SOURCE_UTILS_LOCATION = 'armada.utils.source'

    @mock.patch('armada.utils.source.Git')
    @mock.patch('armada.utils.source.tempfile')
    @mock.patch('armada.utils.source.Repo')
    def test_git_clone_good_url(self, mock_git_repo, mock_temp, mock_git_lib):
        mock_temp.mkdtemp.return_value = '/tmp/armada'
        mock_git_lib.checkout.return_value = "Repository"
        url = 'http://github.com/att-comdev/armada'

        dir = source.git_clone(url)

        self.assertIsNotNone(dir)

    def test_git_clone_empty_url(self):
        url = ''

        with self.assertRaises(Exception):
            self.assertFalse(source.git_clone(url))

    def test_git_clone_bad_url(self):
        url = 'http://github.com/dummy/armada'

        with self.assertRaises(Exception):
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
        with mock.patch('{}.open'.format(self.SOURCE_UTILS_LOCATION),
                        mock_open, create=True):
            source.download_tarball(url)

        mock_temp.mkstemp.assert_called_once()
        mock_requests.get.assert_called_once_with(url)
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
        with self.assertRaises(Exception):
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
        with self.assertRaises(Exception):
            source.source_cleanup(path)
        mock_shutil.rmtree.assert_not_called()
