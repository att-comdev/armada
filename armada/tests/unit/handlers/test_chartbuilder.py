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
import shutil

import fixtures
from hapi.chart.metadata_pb2 import Metadata
import mock
import testtools

from armada.handlers.chartbuilder import ChartBuilder


class ChartBuilderTestCase(testtools.TestCase):
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

    def test_chart_source_clone(self):
        # Don't try to look up .helmignore as that is beyond scope of this
        # test.
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)

        path = os.path.join(chart_dir.path, 'Chart.yaml')
        fd = os.open(path, os.O_CREAT | os.O_WRONLY)
        try:
            os.write(fd, self.chart_yaml.encode('utf-8'))
        finally:
            os.close(fd)

        mock_chart = mock.Mock(source_dir=[chart_dir.path, ''])

        chartbuilder = ChartBuilder(mock_chart)
        resp = chartbuilder.get_metadata()

        self.assertIsInstance(resp, Metadata)

    def test_chart_get_non_template_files(self):
        """Validates that ``get_files()`` ignores 'Chart.yaml', 'values.yaml'
        and 'templates' subfolder and all the files contained therein.
        """

        # Create a temporary directory that represents a chart source directory
        # with various files, including 'Chart.yaml' and 'values.yaml' which
        # should be ignored by `get_files()`.
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)

        for filename in ['foo', 'bar', 'Chart.yaml', 'values.yaml']:
            path = os.path.join(chart_dir.path, filename)
            fd = os.open(path, os.O_CREAT | os.O_WRONLY)
            try:
                os.write(fd, "".encode('utf-8'))
            finally:
                os.close(fd)

        # Create a template directory -- 'templates' -- nested inside the chart
        # directory which should also be ignored.
        template_dir = os.path.join(chart_dir.path, 'templates')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
            self.addCleanup(shutil.rmtree, template_dir)

        for filename in ['template%d' % x for x in range(3)]:
            path = os.path.join(template_dir, filename)
            fd = os.open(path, os.O_CREAT | os.O_WRONLY)
            try:
                os.write(fd, "".encode('utf-8'))
            finally:
                os.close(fd)

        mock_chart = mock.Mock(source_dir=[chart_dir.path, ''])
        chartbuilder = ChartBuilder(mock_chart)

        # Validate that only 'foo' and 'bar' are returned.
        files = chartbuilder.get_files()
        self.assertEqual(['bar', 'foo'], sorted(files))
