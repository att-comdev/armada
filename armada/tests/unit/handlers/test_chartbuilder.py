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

import os
import pytest
import yaml
from supermutes.dot import dotify
from hapi.chart.config_pb2 import Config

from armada.handlers.chartbuilder import ChartBuilder
from armada import errors as ex

basepath = os.path.join(os.path.dirname(__file__))
base_manifest = '{}/templates/simple-chart'.format(basepath)


chart_stream = """
    chart:
        name: mariadb
        release_name: mariadb
        namespace: openstack
        install:
            no_hooks: false
        upgrade:
            no_hooks: false
        values:
            replicas: 1
            volume:
                size: 1Gi
        source:
            type: git
            location: git://github.com/openstack/openstack-helm
            subpath: mariadb
            reference: master
        dependencies: []
        """

chart_yaml = """
apiVersion: v1
description: A Helm chart for Kubernetes
name: hello-world-chart
version: 0.1.0
"""

chart_value = """
# Default values for hello-world-chart.
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.
replicaCount: 1
image:
    repository: nginx
    tag: stable
    pullPolicy: IfNotPresent
service:
    name: nginx
    type: ClusterIP
    externalPort: 38443
    internalPort: 80
resources:
    limits:
        cpu: 100m
        memory: 128Mi
requests:
    cpu: 100m
    memory: 128Mi
"""


def test_chart_source_clone(mocker):

    mock_chartbuilder = mocker.patch.object(ChartBuilder, 'get_source_path')
    mock_chartbuilder.return_value = base_manifest

    mock_chartbuilder2 = mocker.patch.object(ChartBuilder, 'get_ignored_files')
    mock_chartbuilder2.return_value = []

    chart = dotify(yaml.load(chart_stream))

    chartbuilder = ChartBuilder(chart)

    assert chartbuilder.get_source_path() == base_manifest

    resp = chartbuilder.get_metadata()

    assert resp is not None
    assert resp.name == 'simple-chart'

    mock_chartbuilder.return_value = ''

    cb_assert = ChartBuilder(chart)

    assert cb_assert.get_source_path() == ''

    err_message = 'ChartBuilder : Could not find "Chart.yaml" in '

    with pytest.raises(ex.HandlerError, match=err_message):
        assert cb_assert.get_metadata()


def test_chart_source_path(mocker):

    mock_chartbuilder = mocker.patch.object(ChartBuilder, 'get_ignored_files')
    mock_chartbuilder.return_value = []

    document = yaml.load(chart_stream)
    document['source_dir'] = ('/path/', 'new-path')
    chart = dotify(document)

    chartbuilder = ChartBuilder(chart)

    assert chartbuilder.get_source_path() == '/path/new-path'


def test_chart_get_ignored_files(mocker):

    mock_chartbuilder = mocker.patch.object(ChartBuilder, 'get_source_path')
    mock_chartbuilder.return_value = base_manifest

    document = yaml.load(chart_stream)
    chart = dotify(document)
    chartbuilder = ChartBuilder(chart)
    resp = chartbuilder.get_ignored_files()

    expected = ['sample/*', 'NOTES.txt', '*.py', 'ignore_file.sh']

    assert resp == expected

    mock_chartbuilder.return_value = ''

    chartbuilder = ChartBuilder(chart)
    resp = chartbuilder.get_ignored_files()

    assert resp == []


@pytest.mark.parametrize("ignore_file,expected", [
    ('{}/templates/{}'.format(base_manifest, 'NOTE.txt'), False),
    ('{}/templates/{}'.format(base_manifest, 'ignore_file.sh'), False),
    ('{}/templates/{}'.format(base_manifest, 'bash.py'), True),
])
def test_chart_ignore_file(mocker, ignore_file, expected):

    document = yaml.load(chart_stream)
    chart = dotify(document)

    mock_chartbuilder = mocker.patch.object(ChartBuilder, 'get_source_path')
    mock_chartbuilder.return_value = base_manifest
    chartbuilder = ChartBuilder(chart)

    assert chartbuilder.ignore_file(ignore_file) is expected


def test_chartbuild_get_files(mocker):

    document = yaml.load(chart_stream)
    chart = dotify(document)

    mock_chartbuilder = mocker.patch.object(ChartBuilder, 'get_source_path')
    mock_chartbuilder.return_value = base_manifest
    chartbuilder = ChartBuilder(chart)

    assert chartbuilder.get_files() == []


def test_chartbuild_get_values(mocker):

    document = yaml.load(chart_stream)
    chart = dotify(document)

    mock_chartbuilder = mocker.patch.object(ChartBuilder, 'get_source_path')
    mock_chartbuilder.return_value = base_manifest
    chartbuilder = ChartBuilder(chart)

    values_raw = ''
    with open('{}/values.yaml'.format(base_manifest)) as f:
        values_raw = f.read()

    assert chartbuilder.get_values().raw == Config(raw=values_raw).raw

    mock_chartbuilder.return_value = ''
    chartbuilder = ChartBuilder(chart)

    assert chartbuilder.get_values() == Config(raw='')


def test_chartbuild_get_templates(mocker):

    document = yaml.load(chart_stream)
    chart = dotify(document)

    mock_chartbuilder = mocker.patch.object(ChartBuilder, 'get_source_path')
    mock_chartbuilder.return_value = base_manifest
    chartbuilder = ChartBuilder(chart)

    assert len(chartbuilder.get_templates()) == 4
