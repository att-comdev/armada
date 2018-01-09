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

import inspect
import os
import shutil
import yaml

import fixtures
from hapi.chart.chart_pb2 import Chart
from hapi.chart.metadata_pb2 import Metadata
import mock
from supermutes.dot import dotify
import testtools

from armada.handlers.chartbuilder import ChartBuilder


class ChartBuilderTestCase(testtools.TestCase):
    chart_stream = """
        chart:
            chart_name: mariadb
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

    def _write_temporary_file_contents(self, directory, filename, contents):
        path = os.path.join(directory, filename)
        fd = os.open(path, os.O_CREAT | os.O_WRONLY)
        try:
            os.write(fd, contents.encode('utf-8'))
        finally:
            os.close(fd)

    def test_chart_source_clone(self):
        # Create a temporary directory with Chart.yaml that contains data
        # from ``self.chart_yaml``.
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)
        self._write_temporary_file_contents(chart_dir.path, 'Chart.yaml',
                                            self.chart_yaml)

        mock_chart = mock.Mock(source_dir=[chart_dir.path, ''])
        chartbuilder = ChartBuilder(mock_chart)

        # Validate response type is :class:`hapi.chart.metadata_pb2.Metadata`
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
            self._write_temporary_file_contents(chart_dir.path, filename, "")

        # Create a template directory -- 'templates' -- nested inside the chart
        # directory which should also be ignored.
        template_dir = os.path.join(chart_dir.path, 'templates')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
            self.addCleanup(shutil.rmtree, template_dir)
        for filename in ['template%d' % x for x in range(3)]:
            self._write_temporary_file_contents(template_dir, filename, "")

        mock_chart = mock.Mock(source_dir=[chart_dir.path, ''])
        chartbuilder = ChartBuilder(mock_chart)

        expected_files = ('[type_url: "%s"\n, type_url: "%s"\n]' % (
                          os.path.join(chart_dir.path, 'bar'),
                          os.path.join(chart_dir.path, 'foo')))

        # Validate that only 'foo' and 'bar' are returned.
        files = chartbuilder.get_files()
        self.assertEqual(expected_files, repr(files).strip())

    def test_get_basic_helm_chart(self):
        # Before ChartBuilder is executed the `source_dir` points to a
        # directory that was either clone or unpacked from a tarball... pretend
        # that that logic has already been performed.
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)
        self._write_temporary_file_contents(chart_dir.path, 'Chart.yaml',
                                            self.chart_yaml)
        ch = yaml.safe_load(self.chart_stream)['chart']
        ch['source_dir'] = (chart_dir.path, '')

        test_chart = dotify(ch)
        chartbuilder = ChartBuilder(test_chart)
        helm_chart = chartbuilder.get_helm_chart()

        expected = inspect.cleandoc(
            """
            metadata {
              name: "hello-world-chart"
              version: "0.1.0"
              description: "A Helm chart for Kubernetes"
            }
            values {
            }
            """
        ).strip()

        self.assertIsInstance(helm_chart, Chart)
        self.assertTrue(hasattr(helm_chart, 'metadata'))
        self.assertTrue(hasattr(helm_chart, 'values'))
        self.assertEqual(expected, repr(helm_chart).strip())

    def test_get_helm_chart_with_values(self):
        # Before ChartBuilder is executed the `source_dir` points to a
        # directory that was either clone or unpacked from a tarball... pretend
        # that that logic has already been performed.
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)

        self._write_temporary_file_contents(chart_dir.path, 'Chart.yaml',
                                            self.chart_yaml)
        self._write_temporary_file_contents(chart_dir.path, 'values.yaml',
                                            self.chart_value)

        ch = yaml.safe_load(self.chart_stream)['chart']
        ch['source_dir'] = (chart_dir.path, '')

        test_chart = dotify(ch)
        chartbuilder = ChartBuilder(test_chart)
        helm_chart = chartbuilder.get_helm_chart()

        self.assertIsInstance(helm_chart, Chart)
        self.assertTrue(hasattr(helm_chart, 'metadata'))
        self.assertTrue(hasattr(helm_chart, 'values'))
        self.assertTrue(hasattr(helm_chart.values, 'raw'))
        self.assertEqual(self.chart_value, helm_chart.values.raw)

    def test_get_helm_chart_with_files(self):
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)

        # Also create a nested directory and verify that files from it are also
        # added.
        nested_dir = os.path.join(chart_dir.path, 'nested')
        if not os.path.exists(nested_dir):
            os.makedirs(nested_dir)
            self.addCleanup(shutil.rmtree, nested_dir)
        self._write_temporary_file_contents(nested_dir, 'nested0', "random")

        self._write_temporary_file_contents(chart_dir.path, 'Chart.yaml',
                                            self.chart_yaml)
        self._write_temporary_file_contents(chart_dir.path, 'foo', "foobar")
        self._write_temporary_file_contents(chart_dir.path, 'bar', "bazqux")

        ch = yaml.safe_load(self.chart_stream)['chart']
        ch['source_dir'] = (chart_dir.path, '')

        test_chart = dotify(ch)
        chartbuilder = ChartBuilder(test_chart)
        helm_chart = chartbuilder.get_helm_chart()

        expected_files = ('[type_url: "%s"\nvalue: "bazqux"\n, '
                          'type_url: "%s"\nvalue: "foobar"\n, '
                          'type_url: "%s"\nvalue: "random"\n]' % (
                              os.path.join(chart_dir.path, 'bar'),
                              os.path.join(chart_dir.path, 'foo'),
                              os.path.join(nested_dir, 'nested0')))

        self.assertIsInstance(helm_chart, Chart)
        self.assertTrue(hasattr(helm_chart, 'metadata'))
        self.assertTrue(hasattr(helm_chart, 'values'))
        self.assertTrue(hasattr(helm_chart, 'files'))
        self.assertEqual(expected_files, repr(helm_chart.files).strip())

    def test_get_helm_chart_includes_only_relevant_files(self):
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)
        template_dir = os.path.join(chart_dir.path, 'templates')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
            self.addCleanup(shutil.rmtree, template_dir)

        self._write_temporary_file_contents(chart_dir.path, 'Chart.yaml',
                                            self.chart_yaml)
        self._write_temporary_file_contents(chart_dir.path, 'foo', "foobar")
        self._write_temporary_file_contents(chart_dir.path, 'bar', "bazqux")

        # Files to ignore.
        self._write_temporary_file_contents(chart_dir.path, 'values.yaml', "")
        self._write_temporary_file_contents(chart_dir.path, 'Chart.yaml', "")
        for filename in ['template%d' % x for x in range(3)]:
            self._write_temporary_file_contents(template_dir, filename, "")

        ch = yaml.safe_load(self.chart_stream)['chart']
        ch['source_dir'] = (chart_dir.path, '')

        test_chart = dotify(ch)
        chartbuilder = ChartBuilder(test_chart)
        helm_chart = chartbuilder.get_helm_chart()

        expected_files = ('[type_url: "%s"\nvalue: "bazqux"\n, '
                          'type_url: "%s"\nvalue: "foobar"\n]' % (
                              os.path.join(chart_dir.path, 'bar'),
                              os.path.join(chart_dir.path, 'foo')))

        # Validate that only relevant files are included, that the ignored
        # files are present.
        self.assertIsInstance(helm_chart, Chart)
        self.assertTrue(hasattr(helm_chart, 'metadata'))
        self.assertTrue(hasattr(helm_chart, 'values'))
        self.assertTrue(hasattr(helm_chart, 'files'))
        self.assertEqual(expected_files, repr(helm_chart.files).strip())
