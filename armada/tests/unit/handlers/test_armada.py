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
import pytest
import yaml
import os

from armada.handlers.armada import Armada
from armada.handlers.manifest import Manifest

basepath = os.path.join(os.path.dirname(__file__))
base_manifest = '{}/templates/simple.yaml'.format(basepath)

with open(base_manifest) as f:
    test_yaml = f.read()


def test_pre_flight_ops(mocker):
    '''Test pre-flight checks and operations'''

    mock_git = mocker.patch('armada.handlers.armada.source')
    mock_lint = mocker.patch('armada.handlers.armada.lint')
    mock_tiller = mocker.patch('armada.handlers.armada.Tiller')

    armada = Armada('')
    armada.tiller = mock_tiller
    armada.documents = list(yaml.safe_load_all(test_yaml))
    armada.config = Manifest(armada.documents).get_manifest()

    CHART_SOURCES = [
        ('https://github.com/gardlt/hello-world-chart', 'chart_1'),
        ('/tmp/dummy/armada', 'chart_2')]

    # mock methods called by pre_flight_ops()
    mock_tiller.tiller_status.return_value = True
    mock_lint.valid_manifest.return_value = True
    mock_git.git_clone.return_value = CHART_SOURCES[0][0]

    armada.pre_flight_ops()

    mock_git.git_clone.assert_called_once_with(
        CHART_SOURCES[0][0], 'master')

    for group in armada.config.get('armada').get('chart_groups'):
        for counter, chart in enumerate(group.get('chart_group')):
            assert chart.get('chart').get(
                'source_dir')[0] == CHART_SOURCES[counter][0]
            assert chart.get('chart').get(
                'source_dir')[1] == CHART_SOURCES[counter][1]


def test_post_flight_ops(mocker):
    '''Test post-flight operations'''

    mock_git = mocker.patch('armada.handlers.armada.source')
    mock_lint = mocker.patch('armada.handlers.armada.lint')
    mock_tiller = mocker.patch('armada.handlers.armada.Tiller')

    armada = Armada('')
    armada.tiller = mock_tiller
    armada.documents = list(yaml.safe_load_all(test_yaml))
    armada.config = Manifest(armada.documents).get_manifest()

    CHART_SOURCES = [
        ('https://github.com/gardlt/hello-world-chart', 'chart_1'),
        ('/tmp/dummy/armada', 'chart_2')]

    # mock methods called by pre_flight_ops()
    mock_tiller.tiller_status.return_value = True
    mock_lint.valid_manifest.return_value = True
    mock_git.git_clone.return_value = CHART_SOURCES[0][0]

    armada.pre_flight_ops()

    mock_git.git_clone.assert_called_once_with(
        CHART_SOURCES[0][0], 'master')

    armada.pre_flight_ops()

    armada.post_flight_ops()


def test_install(mocker):
    '''Test install functionality from the sync() method'''

    mock_tiller = mocker.patch('armada.handlers.armada.Tiller')
    mock_chartbuilder = mocker.patch('armada.handlers.armada.ChartBuilder')
    # mock_pre_flight = mocker.patch.object(Armada, 'pre_flight_ops')
    # mock_post_flight = mocker.patch.object(Armada, 'post_flight_ops')

    # instantiate Armada and Tiller objects
    armada = Armada('', wait=True, timeout=1000)
    armada.tiller = mock_tiller
    tmp_doc = list(yaml.safe_load_all(test_yaml))
    armada.documents = tmp_doc
    armada.config = Manifest(tmp_doc).get_manifest()

    charts = armada.config['armada']['chart_groups'][0]['chart_group']
    chart_1 = charts[0]['chart']
    chart_2 = charts[1]['chart']

    # mock irrelevant methods called by armada.sync()
    mock_tiller.list_charts.return_value = []
    mock_chartbuilder.get_source_path.return_value = None
    mock_chartbuilder.get_helm_chart.return_value = None

    armada.sync()

    # check params that should be passed to tiller.install_release()
    method_calls = [
        mock.call(
            mock_chartbuilder().get_helm_chart(),
            "{}-{}".format(armada.config['armada']['release_prefix'],
                           chart_1['release']),
            chart_1['namespace'],
            dry_run=armada.dry_run,
            values=yaml.safe_dump(chart_1['values']),
            wait=armada.wait,
            timeout=1000),
        mock.call(
            mock_chartbuilder().get_helm_chart(),
            "{}-{}".format(armada.config['armada']['release_prefix'],
                           chart_2['release']),
            chart_2['namespace'],
            dry_run=armada.dry_run,
            values=yaml.safe_dump(chart_2['values']),
            wait=armada.wait,
            timeout=1000)
    ]
    mock_tiller.install_release.assert_has_calls(method_calls)


@pytest.mark.skip(reason="no way of currently testing this")
def test_upgrade(self):
    '''Test upgrade functionality from the sync() method'''
    # TODO
