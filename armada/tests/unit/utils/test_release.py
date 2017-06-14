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

import unittest

from armada.utils import release as rel

class ReleaseTestCase(unittest.TestCase):

    def test_release_prefix_pass(self):
        expected = 'armada-test'
        prefix, chart = ('armada', 'test')

        assert rel.release_prefix(prefix, chart) == expected

    def test_release_prefix_int_string(self):
        expected = 'armada-4'
        prefix, chart = ('armada', 4)

        assert rel.release_prefix(prefix, chart) == expected

    def test_release_prefix_int_int(self):
        expected = '4-4'
        prefix, chart = (4, 4)

        assert rel.release_prefix(prefix, chart) == expected
