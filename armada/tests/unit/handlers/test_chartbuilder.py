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
import mock
import yaml

from supermutes.dot import dotify

from armada.handlers.chartbuilder import ChartBuilder


class ChartBuilderTestCase(unittest.TestCase):
    chart_stream = yaml.load("""
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
            """)

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

    def test_chartbuilder_source_clone(self):

        chart = dotify(self.chart_stream)
        ChartBuilder.source_clone = mock.Mock(return_value='path')
        chartbuilder = ChartBuilder(chart)
        resp = getattr(chartbuilder, 'source_directory', None)

        self.assertIsNotNone(resp)
        self.assertIsInstance(resp, basestring)

    @mock.patch('armada.handlers.chartbuilder.os')
    def test_chart_source_clone(self, mock_os):

        mock_os.path.join.return_value = self.chart_yaml

        chart = dotify(self.chart_stream)
        ChartBuilder.source_clone = mock.Mock(return_value='path')
        chartbuilder = ChartBuilder(chart)
        resp = chartbuilder.get_metadata()

        self.assertIsNotNone(resp)
        self.assertIsInstance(resp, basestring)
