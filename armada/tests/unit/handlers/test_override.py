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

import copy
import unittest

from armada.exceptions import override_exceptions as ovr_exceptions
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
                            'location': 'http://github.com',
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
                            'location': 'http://github.com',
                            'reference': 'master',
                            'subpath': '.',
                            'type': 'git'
                        },
                        'values': {}
                    }
                }],
                'description': 'Deploys Simple Service',
                'name': 'blog-group',
                'sequenced': 'False'
            }],
            'release_prefix': 'armada'
        }
    }

    def test_chart_override(self):
        '''
        Test chart override for manifest
        '''

        config = copy.deepcopy(self.config)

        # Override test manifest
        override = ['chart.blog-1.source.location=http://gerrithub.io']
        overridden_cfg = Override(config, override).get_manifest()

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
                                'location': 'http://gerrithub.io',
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
                                'location': 'http://github.com',
                                'reference': 'master',
                                'subpath': '.',
                                'type': 'git'
                            },
                            'values': {}
                        }
                    }],
                    'description': 'Deploys Simple Service',
                    'name': 'blog-group',
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

        config = copy.deepcopy(self.config)

        # Override test manifest
        override = ['release_prefix=test']
        overridden_cfg = Override(config, overrides=override).get_manifest()

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
                                'location': 'http://github.com',
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
                                'location': 'http://github.com',
                                'reference': 'master',
                                'subpath': '.',
                                'type': 'git'
                            },
                            'values': {}
                        }
                    }],
                    'description': 'Deploys Simple Service',
                    'name': 'blog-group',
                    'sequenced': 'False'
                }],
                'release_prefix': 'test'
            }
        }

        # Verify overridden config has correct values
        self.assertEqual(overridden_cfg, correct_config)

    def test_chart_group_override(self):
        '''
        Test chart group override for manifest
        '''

        config = copy.deepcopy(self.config)

        # Override test manifest
        override = ['chart_group.blog-group.description=test']
        overridden_cfg = Override(config, overrides=override).get_manifest()

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
                                'location': 'http://github.com',
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
                                'location': 'http://github.com',
                                'reference': 'master',
                                'subpath': '.',
                                'type': 'git'
                            },
                            'values': {}
                        }
                    }],
                    'description': 'test',
                    'name': 'blog-group',
                    'sequenced': 'False'
                }],
                'release_prefix': 'armada'
            }
        }

        # Verify overridden config has correct values
        self.assertEqual(overridden_cfg, correct_config)

    def test_multiple_overrides(self):
        '''
        Test multiple overrides
        '''

        config = copy.deepcopy(self.config)

        # Override test manifest
        override = ['chart.blog-1.source.location=http://gerrithub.io',
                    'chart_group.blog-group.description=test']

        overridden_cfg = Override(config, override).get_manifest()

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
                                'location': 'http://gerrithub.io',
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
                                'location': 'http://github.com',
                                'reference': 'master',
                                'subpath': '.',
                                'type': 'git'
                            },
                            'values': {}
                        }
                    }],
                    'description': 'test',
                    'name': 'blog-group',
                    'sequenced': 'False'
                }],
                'release_prefix': 'armada'
            }
        }

        # Verify overridden config has correct values
        self.assertEqual(overridden_cfg, correct_config)

    @unittest.skip('Issues mocking file')
    def test_value_override(self):
        '''
        Test overriding values with a yaml file
        '''

        config = copy.deepcopy(self.config)

        values = '''
        chart_group:
            blog-group:
                description: test
        chart:
            blog-1:
                source:
                    location: http://gerrithub.io
        '''

        overriden_cfg = Override(config, values='values.yaml').get_manifest()

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
                                'location': 'http://gerrithub.io',
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
                                'location': 'http://github.com',
                                'reference': 'master',
                                'subpath': '.',
                                'type': 'git'
                            },
                            'values': {}
                        }
                    }],
                    'description': 'test',
                    'name': 'blog-group',
                    'sequenced': 'False'
                }],
                'release_prefix': 'armada'
            }
        }

        # Verify overridden config has correct values
        self.assertEqual(overridden_cfg, correct_config)

    def test_invalid_override_type(self):
        '''
        Test invalid override type
        '''

        config = copy.deepcopy(self.config)

        # Override test manifest with bad override type
        override = ['test.bad_value=test']

        # Verify an InvalidOverrideTypeException is raised
        with self.assertRaises(ovr_exceptions.InvalidOverrideTypeException):
            Override(config, override).get_manifest()

    def test_invalid_override_value(self):
        '''
        Test invalid override value
        '''

        config = copy.deepcopy(self.config)

        # Override test manifest with bad override type
        override = ['chart_group.blog-group.chart_group=test']

        # Verify an InvalidOverrideTypeException is raised
        with self.assertRaises(ovr_exceptions.InvalidOverrideValueException):
            Override(config, override).get_manifest()
