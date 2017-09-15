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
import yaml

import testtools

from armada.handlers.armada import Armada
from armada.handlers.manifest import Manifest


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
    name: test_chart_2
    release_name: test_chart_2
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
    name: test_chart_1
    release_name: test_chart_1
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


class ArmadaHandlerTestCase(testtools.TestCase):

    @mock.patch('armada.handlers.armada.Tiller')
    def test_pre_flight_ops(self, mock_tiller):
        '''Test pre-flight checks and operations'''
        armada = Armada('')
        armada.tiller = mock_tiller
        armada.documents = list(yaml.safe_load_all(TEST_YAML))
        armada.config = Manifest(armada.documents).get_manifest()

        CHART_SOURCES = [('git://github.com/dummy/armada', 'chart_1'),
                         ('/tmp/dummy/armada', 'chart_2')]

        # mock methods called by pre_flight_ops()
        mock_tiller.tiller_status.return_value = True

        armada.pre_flight_ops()

        for group in armada.config.get('armada').get('charts'):
            for counter, chart in enumerate(group.get('chart_group')):
                self.assertEqual(
                    chart.get('chart').get('source_dir')[0],
                    CHART_SOURCES[counter][0])
                self.assertEqual(
                    chart.get('chart').get('source_dir')[1],
                    CHART_SOURCES[counter][1])

    # @mock.patch('armada.handlers.armada.git')
    # @mock.patch('armada.handlers.armada.Tiller')
    # def test_post_flight_ops(self, mock_tiller, mock_git):
    #     '''Test post-flight operations'''
    #     armada = Armada('')
    #     armada.tiller = mock_tiller
    #     tmp_doc = yaml.safe_load_all(self.test_yaml)
    #     armada.config = Manifest(tmp_doc).get_manifest()

    #     CHART_SOURCES = [('git://github.com/dummy/armada', 'chart_1'),
    #                      ('/tmp/dummy/armada', 'chart_2')]

    #     # mock methods called by pre_flight_ops()
    #     mock_tiller.tiller_status.return_value = True
    #     mock_git.git_clone.return_value = CHART_SOURCES[0][0]
    #     armada.pre_flight_ops()

    #     armada.post_flight_ops()

    #     for group in yaml.load(self.test_yaml).get('armada').get('charts'):
    #         for counter, chart in enumerate(group.get('chart_group')):
    #             if chart.get('chart').get('source').get('type') == 'git':
    #                 mock_git.source_cleanup \
    #                         .assert_called_with(CHART_SOURCES[counter][0])

    # @mock.patch.object(Armada, 'post_flight_ops')
    # @mock.patch.object(Armada, 'pre_flight_ops')
    # @mock.patch('armada.handlers.armada.ChartBuilder')
    # @mock.patch('armada.handlers.armada.Tiller')
    # def test_install(self, mock_tiller, mock_chartbuilder, mock_pre_flight,
    #                  mock_post_flight):
    #     '''Test install functionality from the sync() method'''

    #     # instantiate Armada and Tiller objects
    #     armada = Armada('', wait=True, timeout=1000)
    #     armada.tiller = mock_tiller
    #     tmp_doc = yaml.safe_load_all(self.test_yaml)
    #     armada.config = Manifest(tmp_doc).get_manifest()

    #     charts = armada.config['armada']['charts'][0]['chart_group']
    #     chart_1 = charts[0]['chart']
    #     chart_2 = charts[1]['chart']

    #     # mock irrelevant methods called by armada.sync()
    #     mock_tiller.list_charts.return_value = []
    #     mock_chartbuilder.get_source_path.return_value = None
    #     mock_chartbuilder.get_helm_chart.return_value = None

    #     armada.sync()

    #     # check params that should be passed to tiller.install_release()
    #     method_calls = [
    #         mock.call(
    #             mock_chartbuilder().get_helm_chart(),
    #             "{}-{}".format(armada.config['armada']['release_prefix'],
    #                            chart_1['release_name']),
    #             chart_1['namespace'],
    #             dry_run=armada.dry_run,
    #             values=yaml.safe_dump(chart_1['values']),
    #             wait=armada.wait,
    #             timeout=1000),
    #         mock.call(
    #             mock_chartbuilder().get_helm_chart(),
    #             "{}-{}".format(armada.config['armada']['release_prefix'],
    #                            chart_2['release_name']),
    #             chart_2['namespace'],
    #             dry_run=armada.dry_run,
    #             values=yaml.safe_dump(chart_2['values']),
    #             wait=armada.wait,
    #             timeout=1000)
    #     ]
    #     mock_tiller.install_release.assert_has_calls(method_calls)

    # def test_upgrade(self):
    #     '''Test upgrade functionality from the sync() method'''
