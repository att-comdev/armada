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
import yaml

from google.protobuf.any_pb2 import Any
from hapi.chart.chart_pb2 import Chart
from hapi.chart.config_pb2 import Config
from hapi.chart.metadata_pb2 import Metadata
from hapi.chart.template_pb2 import Template
from supermutes.dot import dotify

from armada.exceptions import chartbuilder_exceptions

from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

CONF = cfg.CONF


class ChartBuilder(object):
    '''
    This class handles taking chart intentions as a parameter and
    turning those into proper protoc helm charts that can be
    pushed to tiller.

    It also processes chart source declarations, fetching chart
    source from external resources where necessary
    '''

    def __init__(self, chart, parent=None):
        '''
        Initialize the ChartBuilder class

        Note that tthis will trigger a source pull as part of
        initialization as its necessary in order to examine
        the source service many of the calls on ChartBuilder
        '''

        # cache for generated protoc chart object
        self._helm_chart = None

        # record whether this is a dependency based chart
        self.parent = parent

        # store chart schema
        self.chart = chart

        # extract, pull, whatever the chart from its source
        self.source_directory = self.get_source_path()

        # load ignored files from .helmignore if present
        self.ignored_files = self.get_ignored_files()

    def get_source_path(self):
        '''
        Return the joined path of the source directory and subpath
        '''
        return (
            os.path.join(self.chart.source_dir[0], self.chart.source_dir[1])
            if (hasattr(self.chart, 'source_dir') and
                isinstance(self.chart.source_dir, (list, tuple)) and
                len(self.chart.source_dir) == 2)
            else ""
        )

    def get_ignored_files(self):
        '''
        Load files from .helmignore if present
        '''
        try:
            ignored_files = []
            if os.path.exists(os.path.join(self.source_directory,
                                           '.helmignore')):
                with open(os.path.join(self.source_directory,
                                       '.helmignore')) as f:
                    ignored_files = f.readlines()
            return [filename.strip() for filename in ignored_files]
        except Exception:
            raise chartbuilder_exceptions.IgnoredFilesLoadException()

    def ignore_file(self, filename):
        '''
        :params file - filename to compare against list of ignored files

        Returns true if file matches an ignored file wildcard or exact name,
         false otherwise
        '''
        for ignored_file in self.ignored_files:
            if (ignored_file.startswith('*') and
                    filename.endswith(ignored_file.strip('*'))):
                return True
            elif ignored_file == filename:
                return True
        return False

    def get_metadata(self):
        '''
        Process metadata
        '''
        # extract Chart.yaml to construct metadata

        try:
            with open(os.path.join(self.source_directory, 'Chart.yaml')) as f:
                chart_yaml = dotify(yaml.safe_load(f.read().encode('utf-8')))

        except Exception:
            raise chartbuilder_exceptions.MetadataLoadException()

        # construct Metadata object
        return Metadata(
            description=chart_yaml.description,
            name=chart_yaml.name,
            version=chart_yaml.version)

    def get_files(self):
        '''
        Return (non-template) files in this chart.

        Non-template files include all files **not** under templates and
        charts subfolders, except: Chart.yaml, values.yaml, values.toml and
        charts/.prov

        The class :class:`google.protobuf.any_pb2.Any` is wrapped around
        each file as that is what Helm uses.

        For more information, see:
        https://github.com/kubernetes/helm/blob/fa06dd176dbbc247b40950e38c09f978efecaecc/pkg/chartutil/load.go

        :returns: List of non-template files.
        :rtype: List[:class:`google.protobuf.any_pb2.Any`]
        '''

        files_to_ignore = ['Chart.yaml', 'values.yaml', 'values.toml']
        non_template_files = []

        def _append_file_to_result(root, rel_folder_path, file):
            abspath = os.path.abspath(os.path.join(root, file))
            relpath = os.path.join(rel_folder_path, file)

            with open(abspath, 'r') as f:
                file_contents = f.read().encode('utf-8')
            non_template_files.append(
                Any(type_url=relpath,
                    value=file_contents))

        for root, dirs, files in os.walk(self.source_directory):
            relfolder = os.path.split(root)[-1]
            rel_folder_path = os.path.relpath(root, self.source_directory)

            if relfolder not in ['charts', 'templates']:
                for file in files:
                    if (file not in files_to_ignore and
                            file not in non_template_files):
                        _append_file_to_result(root, rel_folder_path, file)
            elif relfolder == 'charts' and '.prov' in files:
                _append_file_to_result(root, rel_folder_path, '.prov')

        return non_template_files

    def get_values(self):
        '''
        Return the chart (default) values
        '''

        # create config object representing unmarshaled values.yaml
        if os.path.exists(os.path.join(self.source_directory, 'values.yaml')):
            with open(os.path.join(self.source_directory, 'values.yaml')) as f:
                raw_values = f.read()
        else:
            LOG.warn("No values.yaml in %s, using empty values",
                     self.source_directory)
            raw_values = ''

        return Config(raw=raw_values)

    def get_templates(self):
        '''
        Return all the chart templates
        '''

        # process all files in templates/ as a template to attach to the chart
        # building a Template object
        templates = []
        if not os.path.exists(
                os.path.join(self.source_directory, 'templates')):
            LOG.warn("Chart %s has no templates directory. "
                     "No templates will be deployed", self.chart.chart_name)
        for root, _, files in os.walk(
                os.path.join(self.source_directory, 'templates'),
                topdown=True):
            for tpl_file in files:
                tname = os.path.relpath(
                    os.path.join(root, tpl_file),
                    os.path.join(self.source_directory, 'templates'))
                if self.ignore_file(tname):
                    LOG.debug('Ignoring file %s', tname)
                    continue

                with open(os.path.join(root, tpl_file)) as f:
                    templates.append(
                        Template(name=tname, data=f.read().encode()))

        return templates

    def get_helm_chart(self):
        '''
        Return a helm chart object
        '''
        if self._helm_chart:
            return self._helm_chart

        dependencies = []
        for dep in self.chart.dependencies:
            LOG.info("Building dependency chart %s for release %s.",
                     dep.chart.chart_name, dep.chart.release)
            try:
                dependencies.append(ChartBuilder(dep.chart).get_helm_chart())
            except Exception:
                chart_name = self.chart.chart_name
                raise chartbuilder_exceptions.DependencyException(chart_name)

        try:
            helm_chart = Chart(
                metadata=self.get_metadata(),
                templates=self.get_templates(),
                dependencies=dependencies,
                values=self.get_values(),
                files=self.get_files())
        except Exception:
            chart_name = self.chart.chart_name
            raise chartbuilder_exceptions.HelmChartBuildException(chart_name)

        self._helm_chart = helm_chart
        return helm_chart

    def dump(self):
        '''
        This method is used to dump a chart object as a
        serialized string so that we can perform a diff

        It should recurse into dependencies
        '''
        return self.get_helm_chart().SerializeToString()
