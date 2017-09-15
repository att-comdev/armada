# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
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
import yaml

import testtools

from armada.handlers import armada


TEST_YAML = """
---
schema: armada/Manifest/v1
metadata:
  schema: metadata/Document/v1
  name: example-manifest
data:
  release_prefix: armada
  chart_groups:
    - example-group
---
schema: armada/ChartGroup/v1
metadata:
  schema: metadata/Document/v1
  name: example-group
data:
  description: this is a test
  sequenced: False
  chart_group:
    - example-chart-1
    - example-chart-2
---
schema: armada/Chart/v1
metadata:
  schema: metadata/Document/v1
  name: example-chart-2
data:
    chart_name: test_chart_2
    release: test_chart_2
    namespace: test
    values: {}
    source:
      type: local
      location: /tmp/dummy/armada
      subpath: chart_2
      reference: null
    dependencies: []
    timeout: 5
---
schema: armada/Chart/v1
metadata:
  schema: metadata/Document/v1
  name: example-chart-1
data:
    chart_name: test_chart_1
    release: test_chart_1
    namespace: test
    values: {}
    source:
      type: git
      location: git://github.com/dummy/armada
      subpath: chart_1
      reference: master
    dependencies: []
    timeout: 50
"""

CHART_SOURCES = [('git://github.com/dummy/armada', 'chart_1'),
                 ('/tmp/dummy/armada', 'chart_2')]


class ArmadaHandlerTestCase(testtools.TestCase):

    def _test_pre_flight_ops(self, armada_obj):
        armada_obj.pre_flight_ops()

        expected_config = {
            'armada': {
                'release_prefix': 'armada',
                'chart_groups': [
                    {
                        'chart_group': [
                            {
                                'chart': {
                                    'dependencies': [],
                                    'chart_name': 'test_chart_1',
                                    'namespace': 'test',
                                    'release': 'test_chart_1',
                                    'source': {
                                        'location': (
                                            'git://github.com/dummy/armada'),
                                        'reference': 'master',
                                        'subpath': 'chart_1',
                                        'type': 'git'
                                    },
                                    'source_dir': CHART_SOURCES[0],
                                    'timeout': 50,
                                    'values': {}
                                }
                            },
                            {
                                'chart': {
                                    'dependencies': [],
                                    'chart_name': 'test_chart_2',
                                    'namespace': 'test',
                                    'release': 'test_chart_2',
                                    'source': {
                                        'location': '/tmp/dummy/armada',
                                        'reference': None,
                                        'subpath': 'chart_2',
                                        'type': 'local'
                                    },
                                    'source_dir': CHART_SOURCES[1],
                                    'timeout': 5,
                                    'values': {}
                                }
                            }
                        ],
                        'description': 'this is a test',
                        'name': 'example-group',
                        'sequenced': False
                    }
                ]
            }
        }

        self.assertTrue(hasattr(armada_obj, 'config'))
        self.assertIsInstance(armada_obj.config, dict)
        self.assertIn('armada', armada_obj.config)
        self.assertEqual(expected_config, armada_obj.config)

    @mock.patch.object(armada, 'source')
    @mock.patch('armada.handlers.armada.Tiller')
    def test_pre_flight_ops(self, mock_tiller, mock_source):
        """Test pre-flight checks and operations."""
        yaml_documents = list(yaml.safe_load_all(TEST_YAML))
        armada_obj = armada.Armada(yaml_documents)

        # Mock methods called by `pre_flight_ops()`.
        mock_tiller.tiller_status.return_value = True
        mock_source.git_clone.return_value = CHART_SOURCES[0][0]

        self._test_pre_flight_ops(armada_obj)

        mock_tiller.assert_called_once_with(tiller_host=None,
                                            tiller_port=44134)
        mock_source.git_clone.assert_called_once_with(
            'git://github.com/dummy/armada', 'master')

    @mock.patch.object(armada, 'source')
    @mock.patch('armada.handlers.armada.Tiller')
    def test_post_flight_ops(self, mock_tiller, mock_source):
        """Test post-flight operations."""
        yaml_documents = list(yaml.safe_load_all(TEST_YAML))
        armada_obj = armada.Armada(yaml_documents)

        # Mock methods called by `pre_flight_ops()`.
        mock_tiller.tiller_status.return_value = True
        mock_source.git_clone.return_value = CHART_SOURCES[0][0]

        self._test_pre_flight_ops(armada_obj)

        armada_obj.post_flight_ops()

        for group in armada_obj.config['armada']['chart_groups']:
            for counter, chart in enumerate(group.get('chart_group')):
                if chart.get('chart').get('source').get('type') == 'git':
                    mock_source.source_cleanup.assert_called_with(
                        CHART_SOURCES[counter][0])

    @mock.patch.object(armada.Armada, 'post_flight_ops')
    @mock.patch.object(armada.Armada, 'pre_flight_ops')
    @mock.patch('armada.handlers.armada.ChartBuilder')
    @mock.patch('armada.handlers.armada.Tiller')
    def test_install(self, mock_tiller, mock_chartbuilder, mock_pre_flight,
                     mock_post_flight):
        '''Test install functionality from the sync() method'''

        # Instantiate Armada object.
        yaml_documents = list(yaml.safe_load_all(TEST_YAML))
        armada_obj = armada.Armada(yaml_documents)

        charts = armada_obj.config['armada']['chart_groups'][0]['chart_group']
        chart_1 = charts[0]['chart']
        chart_2 = charts[1]['chart']

        # Mock irrelevant methods called by `armada.sync()`.
        mock_tiller.list_charts.return_value = []
        mock_chartbuilder.get_source_path.return_value = None
        mock_chartbuilder.get_helm_chart.return_value = None

        armada_obj.sync()

        # Check params that should be passed to `tiller.install_release()`.
        method_calls = [
            mock.call(
                mock_chartbuilder().get_helm_chart(),
                "{}-{}".format(armada_obj.config['armada']['release_prefix'],
                               chart_1['release']),
                chart_1['namespace'],
                dry_run=armada_obj.dry_run,
                values=yaml.safe_dump(chart_1['values']),
                wait=armada_obj.wait,
                timeout=armada_obj.timeout),
            mock.call(
                mock_chartbuilder().get_helm_chart(),
                "{}-{}".format(armada_obj.config['armada']['release_prefix'],
                               chart_2['release']),
                chart_2['namespace'],
                dry_run=armada_obj.dry_run,
                values=yaml.safe_dump(chart_2['values']),
                wait=armada_obj.wait,
                timeout=armada_obj.timeout)
        ]
        mock_tiller.return_value.install_release.assert_has_calls(method_calls)
