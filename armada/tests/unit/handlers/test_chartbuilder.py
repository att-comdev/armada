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
from armada.exceptions import chartbuilder_exceptions


class ChartBuilderTestCase(testtools.TestCase):
    chart_yaml = """
        apiVersion: v1
        description: A sample Helm chart for Kubernetes
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

    chart_stream = """
        chart:
            chart_name: mariadb
            release: mariadb
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

    dependency_chart_yaml = """
        apiVersion: v1
        description: Another sample Helm chart for Kubernetes
        name: dependency-chart
        version: 0.1.0
    """

    dependency_chart_stream = """
        chart:
            chart_name: keystone
            release: keystone
            namespace: undercloud
            timeout: 100
            install:
                no_hooks: false
            upgrade:
                no_hooks: false
            values: {}
            source:
                type: git
                location: git://github.com/example/example
                subpath: example-chart
                reference: master
            dependencies: []
    """

    def _write_temporary_file_contents(self, directory, filename, contents):
        path = os.path.join(directory, filename)
        fd = os.open(path, os.O_CREAT | os.O_WRONLY)
        try:
            os.write(fd, contents.encode('utf-8'))
        finally:
            os.close(fd)

    def _make_temporary_subdirectory(self, parent_path, sub_path):
        subdir = os.path.join(parent_path, sub_path)
        if not os.path.exists(subdir):
            os.makedirs(subdir)
            self.addCleanup(shutil.rmtree, subdir)
        return subdir

    def test_source_clone(self):
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

    def test_get_metadata_with_incorrect_file_invalid(self):
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)

        mock_chart = mock.Mock(source_dir=[chart_dir.path, ''])
        chartbuilder = ChartBuilder(mock_chart)

        self.assertRaises(
            chartbuilder_exceptions.MetadataLoadException,
            chartbuilder.get_metadata)

    def test_get_files(self):
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
        templates_subdir = self._make_temporary_subdirectory(
            chart_dir.path, 'templates')
        for filename in ['template%d' % x for x in range(3)]:
            self._write_temporary_file_contents(templates_subdir, filename, "")

        mock_chart = mock.Mock(source_dir=[chart_dir.path, ''])
        chartbuilder = ChartBuilder(mock_chart)

        expected_files = ('[type_url: "%s"\n, type_url: "%s"\n]' % ('./bar',
                                                                    './foo'))
        # Validate that only 'foo' and 'bar' are returned.
        actual_files = sorted(chartbuilder.get_files(),
                              key=lambda x: x.type_url)
        self.assertEqual(expected_files, repr(actual_files).strip())

    def test_get_files_with_unicode_characters(self):
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)
        for filename in ['foo', 'bar', 'Chart.yaml', 'values.yaml']:
            self._write_temporary_file_contents(
                chart_dir.path, filename, "DIRC^@^@^@^B^@^@^@×Z®<86>F.1")

        mock_chart = mock.Mock(source_dir=[chart_dir.path, ''])
        chartbuilder = ChartBuilder(mock_chart)

        chartbuilder.get_files()

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
              description: "A sample Helm chart for Kubernetes"
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
        # Create a chart directory with some test files.
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)
        # Chart.yaml is mandatory for `ChartBuilder.get_metadata`.
        self._write_temporary_file_contents(chart_dir.path, 'Chart.yaml',
                                            self.chart_yaml)
        self._write_temporary_file_contents(chart_dir.path, 'foo', "foobar")
        self._write_temporary_file_contents(chart_dir.path, 'bar', "bazqux")

        # Also create a nested directory and verify that files from it are also
        # added.
        nested_dir = self._make_temporary_subdirectory(
            chart_dir.path, 'nested')
        self._write_temporary_file_contents(nested_dir, 'nested0', "random")

        ch = yaml.safe_load(self.chart_stream)['chart']
        ch['source_dir'] = (chart_dir.path, '')

        test_chart = dotify(ch)
        chartbuilder = ChartBuilder(test_chart)
        helm_chart = chartbuilder.get_helm_chart()

        expected_files = ('[type_url: "%s"\nvalue: "bazqux"\n, '
                          'type_url: "%s"\nvalue: "foobar"\n, '
                          'type_url: "%s"\nvalue: "random"\n]' %
                          ('./bar', './foo', 'nested/nested0'))

        self.assertIsInstance(helm_chart, Chart)
        self.assertTrue(hasattr(helm_chart, 'metadata'))
        self.assertTrue(hasattr(helm_chart, 'values'))
        self.assertTrue(hasattr(helm_chart, 'files'))
        actual_files = sorted(helm_chart.files, key=lambda x: x.value)
        self.assertEqual(expected_files, repr(actual_files).strip())

    def test_get_helm_chart_includes_only_relevant_files(self):
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)

        templates_subdir = self._make_temporary_subdirectory(
            chart_dir.path, 'templates')
        charts_subdir = self._make_temporary_subdirectory(
            chart_dir.path, 'charts')
        templates_nested_subdir = self._make_temporary_subdirectory(
            templates_subdir, 'bin')
        charts_nested_subdir = self._make_temporary_subdirectory(
            charts_subdir, 'extra')

        self._write_temporary_file_contents(chart_dir.path, 'Chart.yaml',
                                            self.chart_yaml)
        self._write_temporary_file_contents(chart_dir.path, 'foo', "foobar")
        self._write_temporary_file_contents(chart_dir.path, 'bar', "bazqux")

        # Files to ignore within top-level directory.
        files_to_ignore = ['Chart.yaml', 'values.yaml', 'values.toml']
        for file in files_to_ignore:
            self._write_temporary_file_contents(chart_dir.path, file, "")
        file_to_ignore = 'file_to_ignore'
        # Files to ignore within templates/ subdirectory.
        self._write_temporary_file_contents(
            templates_subdir, file_to_ignore, "")
        # Files to ignore within charts/ subdirectory.
        self._write_temporary_file_contents(
            charts_subdir, file_to_ignore, "")
        # Files to ignore within templates/bin subdirectory.
        self._write_temporary_file_contents(
            templates_nested_subdir, file_to_ignore, "")
        # Files to ignore within charts/extra subdirectory.
        self._write_temporary_file_contents(
            charts_nested_subdir, file_to_ignore, "")
        # Files to **include** within charts/ subdirectory.
        self._write_temporary_file_contents(
            charts_subdir, '.prov', "xyzzy")

        ch = yaml.safe_load(self.chart_stream)['chart']
        ch['source_dir'] = (chart_dir.path, '')

        test_chart = dotify(ch)
        chartbuilder = ChartBuilder(test_chart)
        helm_chart = chartbuilder.get_helm_chart()

        expected_files = ('[type_url: "%s"\nvalue: "bazqux"\n, '
                          'type_url: "%s"\nvalue: "foobar"\n, '
                          'type_url: "%s"\nvalue: "xyzzy"\n]' %
                          ('./bar', './foo', 'charts/.prov'))

        # Validate that only relevant files are included, that the ignored
        # files are present.
        self.assertIsInstance(helm_chart, Chart)
        self.assertTrue(hasattr(helm_chart, 'metadata'))
        self.assertTrue(hasattr(helm_chart, 'values'))
        self.assertTrue(hasattr(helm_chart, 'files'))
        actual_files = sorted(helm_chart.files, key=lambda x: x.value)
        self.assertEqual(expected_files, repr(actual_files).strip())

    def test_get_helm_chart_with_dependencies(self):
        # Main chart directory and files.
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)
        self._write_temporary_file_contents(chart_dir.path, 'Chart.yaml',
                                            self.chart_yaml)
        ch = yaml.safe_load(self.chart_stream)['chart']
        ch['source_dir'] = (chart_dir.path, '')

        # Dependency chart directory and files.
        dep_chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, dep_chart_dir.path)
        self._write_temporary_file_contents(dep_chart_dir.path, 'Chart.yaml',
                                            self.dependency_chart_yaml)
        dep_ch = yaml.safe_load(self.dependency_chart_stream)
        dep_ch['chart']['source_dir'] = (dep_chart_dir.path, '')

        main_chart = dotify(ch)
        dependency_chart = dotify(dep_ch)
        main_chart.dependencies = [dependency_chart]

        chartbuilder = ChartBuilder(main_chart)
        helm_chart = chartbuilder.get_helm_chart()

        expected_dependency = inspect.cleandoc("""
            metadata {
              name: "dependency-chart"
              version: "0.1.0"
              description: "Another sample Helm chart for Kubernetes"
            }
            values {
            }
        """).strip()

        expected = inspect.cleandoc("""
            metadata {
              name: "hello-world-chart"
              version: "0.1.0"
              description: "A sample Helm chart for Kubernetes"
            }
            dependencies {
              metadata {
                name: "dependency-chart"
                version: "0.1.0"
                description: "Another sample Helm chart for Kubernetes"
              }
              values {
              }
            }
            values {
            }
        """).strip()

        # Validate the main chart.
        self.assertIsInstance(helm_chart, Chart)
        self.assertTrue(hasattr(helm_chart, 'metadata'))
        self.assertTrue(hasattr(helm_chart, 'values'))
        self.assertEqual(expected, repr(helm_chart).strip())

        # Validate the dependency chart.
        self.assertTrue(hasattr(helm_chart, 'dependencies'))
        self.assertEqual(1, len(helm_chart.dependencies))

        dep_helm_chart = helm_chart.dependencies[0]
        self.assertIsInstance(dep_helm_chart, Chart)
        self.assertTrue(hasattr(dep_helm_chart, 'metadata'))
        self.assertTrue(hasattr(dep_helm_chart, 'values'))
        self.assertEqual(expected_dependency, repr(dep_helm_chart).strip())

    def test_dump(self):
        # Validate base case.
        chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, chart_dir.path)
        self._write_temporary_file_contents(chart_dir.path, 'Chart.yaml',
                                            self.chart_yaml)
        ch = yaml.safe_load(self.chart_stream)['chart']
        ch['source_dir'] = (chart_dir.path, '')

        test_chart = dotify(ch)
        chartbuilder = ChartBuilder(test_chart)
        self.assertRegex(
            repr(chartbuilder.dump()),
            'hello-world-chart.*A sample Helm chart for Kubernetes.*')

        # Validate recursive case (with dependencies).
        dep_chart_dir = self.useFixture(fixtures.TempDir())
        self.addCleanup(shutil.rmtree, dep_chart_dir.path)
        self._write_temporary_file_contents(dep_chart_dir.path, 'Chart.yaml',
                                            self.dependency_chart_yaml)
        dep_ch = yaml.safe_load(self.dependency_chart_stream)
        dep_ch['chart']['source_dir'] = (dep_chart_dir.path, '')

        dependency_chart = dotify(dep_ch)
        test_chart.dependencies = [dependency_chart]
        chartbuilder = ChartBuilder(test_chart)

        re = inspect.cleandoc("""
            hello-world-chart.*A sample Helm chart for Kubernetes.*
            dependency-chart.*Another sample Helm chart for Kubernetes.*
        """).replace('\n', '').strip()
        self.assertRegex(repr(chartbuilder.dump()), re)
