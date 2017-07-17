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

from armada.utils import git

class GitTestCase(unittest.TestCase):

    @mock.patch('armada.utils.git.tempfile')
    @mock.patch('armada.utils.git.pygit2')
    def test_git_clone_repo_pass(self, mock_pygit, mock_temp):
        mock_temp.mkdtemp.return_value = '/tmp/armada'
        mock_pygit.clone_repository.return_value = "Repository"
        url = 'http://github.com/att-comdev/armada'
        dir = git.git_clone(url)

        self.assertIsNotNone(dir)

    def test_git_clone_empty_url(self):
        url = ''
        dir = git.git_clone(url)

        self.assertFalse(dir)

    def test_git_clone_bad_url(self):
        url = 'http://github.com/dummy/armada'
        dir = git.git_clone(url)

        self.assertFalse(dir)

    def test_check_available_repo_pass(self):
        url = 'http://github.com/att-comdev/armada'
        resp = git.check_available_repo(url)

        self.assertTrue(resp)

    def test_check_available_repo_dummy_url(self):
        url = 'http://github.com/dummy/armada'
        resp = git.check_available_repo(url)
        self.assertFalse(resp)
