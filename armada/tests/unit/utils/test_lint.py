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
import yaml

from armada.utils import lint

class LintTestCase(unittest.TestCase):

    def test_lint_armada_yaml_pass(self):
        config = yaml.load("""
        armada:
            release_prefix: armada-test
            charts:
                - chart:
                    name: chart
                    release_name: chart
                    namespace: chart
        """)
        resp = lint.valid_manifest(config)
        self.assertTrue(resp)

    def test_lint_armada_keyword_removed(self):
        config = yaml.load("""
        armasda:
            release_prefix: armada-test
            charts:
                - chart:
                    name: chart
                    release_name: chart
                    namespace: chart
        """)

        with self.assertRaises(Exception):
            lint.valid_manifest(config)

    def test_lint_prefix_keyword_removed(self):
        config = yaml.load("""
        armada:
            release: armada-test
            charts:
                - chart:
                    name: chart
                    release_name: chart
                    namespace: chart
        """)

        with self.assertRaises(Exception):
            lint.valid_manifest(config)

    def test_lint_armada_removed(self):
        config = yaml.load("""
        armasda:
            release_prefix: armada-test
            chart:
                - chart:
                    name: chart
                    release_name: chart
                    namespace: chart
        """)

        with self.assertRaises(Exception):
            lint.valid_manifest(config)
