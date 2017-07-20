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

from armada.exceptions import git_exceptions

from armada.utils import git

class GitTestCase(unittest.TestCase):

    @mock.patch('armada.utils.git.tempfile')
    @mock.patch('armada.utils.git.pygit2')
    def test_git_clone_good_url(self, mock_pygit, mock_temp):
        mock_temp.mkdtemp.return_value = '/tmp/armada'
        mock_pygit.clone_repository.return_value = "Repository"
        url = 'http://github.com/att-comdev/armada'
        dir = git.git_clone(url)

        self.assertIsNotNone(dir)

    def test_git_clone_empty_url(self):
        url = ''

        with self.assertRaises(Exception):
            self.assertFalse(git.git_clone(url))

    def test_git_clone_bad_url(self):
        url = 'http://github.com/dummy/armada'

        with self.assertRaises(Exception):
            git.git_clone(url)

    @mock.patch('armada.utils.git.shutil')
    @mock.patch('armada.utils.git.path')
    def test_source_cleanup(self, mock_path, mock_shutil):
        mock_path.exists.return_value = True
        path = 'armada'

        try:
            git.source_cleanup(path)
        except git_exceptions.SourceCleanupException:
            pass

        mock_shutil.rmtree.assert_called_with(path)

    @mock.patch('armada.utils.git.shutil')
    @mock.patch('armada.utils.git.path')
    def test_source_cleanup_bad_path(self, mock_path, mock_shutil):
        mock_path.exists.return_value = False
        path = 'armada'
        with self.assertRaises(Exception):
            git.source_cleanup(path)
        mock_shutil.rmtree.assert_not_called()
