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

from armada.handlers.override import Override

class OverrideTestCase(unittest.TestCase):

    config = {
        'armada': {
            'chart_groups': [{
                'chart_group': [{
                    'chart': {
                        'chart_name': 'blog-1',
                        'dependencies': [],
                        'namespace': 'default',
                        'release': 'blog-1',
                        'source': {
                            'location': 'http://repo-url',
                            'reference': 'master',
                            'subpath': '.',
                            'type': 'git'
                        },
                        'values': {}
                    },
                    'chart': {
                        'chart_name': 'blog-2',
                        'dependencies': [],
                        'namespace': 'default',
                        'release': 'blog-1',
                        'source': {
                            'location': 'http://repo-url',
                            'reference': 'master',
                            'subpath': '.',
                            'type': 'git'
                        },
                        'values': {}
                    }
                }],
                'description': 'Deploys Simple Service',
                'sequenced': 'False'
            }],
            'release_prefix': 'armada'
        }
    }

    def test_chart_override(self):
        '''
        Test chart override for manifest
        '''

        # Override test manifest
        chart_override = 'chart.blog-1.source.location=http://phony-url.com'
        overridden_cfg = Override(self.config, chart_override).get_manifest()

        # Overriden config expected result
        correct_config = {
            'armada': {
                'chart_groups': [{
                    'chart_group': [{
                        'chart': {
                            'chart_name': 'blog-1',
                            'dependencies': [],
                            'namespace': 'default',
                            'release': 'blog-1',
                            'source': {
                                'location': 'http://phony-url.com',
                                'reference': 'master',
                                'subpath': '.',
                                'type': 'git'
                            },
                            'values': {}
                        },
                        'chart': {
                            'chart_name': 'blog-2',
                            'dependencies': [],
                            'namespace': 'default',
                            'release': 'blog-1',
                            'source': {
                                'location': 'http://repo-url',
                                'reference': 'master',
                                'subpath': '.',
                                'type': 'git'
                            },
                            'values': {}
                        }
                    }],
                    'description': 'Deploys Simple Service',
                    'sequenced': 'False'
                }],
                'release_prefix': 'armada'
            }
        }

        # Verify overridden config has correct values
        self.assertEqual(overridden_cfg, correct_config)

    def test_prefix_override(self):
        '''
        Test prefix override for manifest
        '''

        # Override test manifest
        chart_override = 'release_prefix=Test Release'
        overridden_cfg = Override(self.config, chart_override).get_manifest()

        # Overriden config expected result
        correct_config = {
            'armada': {
                'chart_groups': [{
                    'chart_group': [{
                        'chart': {
                            'chart_name': 'blog-1',
                            'dependencies': [],
                            'namespace': 'default',
                            'release': 'blog-1',
                            'source': {
                                'location': 'http://phony-url.com',
                                'reference': 'master',
                                'subpath': '.',
                                'type': 'git'
                            },
                            'values': {}
                        },
                        'chart': {
                            'chart_name': 'blog-2',
                            'dependencies': [],
                            'namespace': 'default',
                            'release': 'blog-1',
                            'source': {
                                'location': 'http://repo-url',
                                'reference': 'master',
                                'subpath': '.',
                                'type': 'git'
                            },
                            'values': {}
                        }
                    }],
                    'description': 'Deploys Simple Service',
                    'sequenced': 'False'
                }],
                'release_prefix': 'Test Release'
            }
        }

        # Verify overridden config has correct values
        self.assertEqual(overridden_cfg, correct_config)
