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

from hapi.chart.template_pb2 import Template
from hapi.chart.chart_pb2 import Chart
from hapi.chart.metadata_pb2 import Metadata
from hapi.chart.config_pb2 import Config
from supermutes.dot import dotify
import logging
import shutil
import tempfile
import pygit2
import os
import yaml

LOG = logging.getLogger(__name__)

class ChartBuilder(object):
    '''
    This class handles taking chart intentions as a paramter and
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
        self.source_directory = self.source_clone()

    def source_clone(self):
        '''
        Clone the charts source

        We only support a git source type right now, which can also
        handle git:// local paths as well
        '''

        if self.chart.source.type == 'git':

            tmpdir = tempfile.mkdtemp(prefix='armada', dir='/tmp')
            self._source_tmp_dir = tmpdir
            if self.parent:
                LOG.info("Cloning %s/%s as dependency for %s",
                         self.chart.source.location,
                         self.chart.source.subpath,
                         self.parent)
            else:
                LOG.info("Cloning %s/%s for release %s",
                         self.chart.source.location,
                         self.chart.source.subpath,
                         self.chart.release_name)

            pygit2.clone_repository(self.chart.source.location, tmpdir)
            return os.path.join(tmpdir, self.chart.source.subpath)

        else:
            LOG.exception("Unknown source type %s for chart %s",
                          self.chart.name,
                          self.chart.source.type)

    def source_cleanup(self):
        '''
        Cleanup source
        '''
        shutil.rmtree(self._source_tmp_dir)

    def get_metadata(self):
        '''
        Process metadata
        '''
        # extract Chart.yaml to construct metadata
        chart_yaml = dotify(yaml.load(open(
            os.path.join(self.source_directory, 'Chart.yaml')).read()))

        # construct Metadata object
        return Metadata(
            description=chart_yaml.description,
            name=chart_yaml.name,
            version=chart_yaml.version
        )

    def get_files(self):
        '''
        Return (non-template) files in this chart

        TODO(alanmeadows): Not implemented
        '''
        return []

    def get_values(self):
        '''
        Return the chart (default) values
        '''

        # create config object representing unmarshaled values.yaml
        if os.path.exists(os.path.join(self.source_directory, 'values.yaml')):
            raw_values = open(os.path.join(self.source_directory,
                                           'values.yaml')).read()
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
        if not os.path.exists(os.path.join(self.source_directory,
                                           'templates')):
            LOG.warn("Chart %s has no templates directory,"
                     "no templates will be deployed", self.chart.name)
        for root, _, files in os.walk(os.path.join(self.source_directory,
                                                   'templates'), topdown=True):
            for tpl_file in files:
                templates.append(Template(name=tpl_file,
                                          data=open(os.path.join(root,
                                                                 tpl_file),
                                                    'r').read()))
        return templates

    def get_helm_chart(self):
        '''
        Return a helm chart object
        '''

        if self._helm_chart:
            return self._helm_chart
        # dependencies
        # [process_chart(x, is_dependency=True) for x in chart.dependencies]
        dependencies = []

        for chart in self.chart.dependencies:
            LOG.info("Building dependency chart %s for release %s", chart.name,
                     self.chart.release_name)
            dependencies.append(ChartBuilder(chart).get_helm_chart())

        helm_chart = Chart(
            metadata=self.get_metadata(),
            templates=self.get_templates(),
            dependencies=dependencies,
            values=self.get_values(),
            files=self.get_files(),
        )

        self._helm_chart = helm_chart
        return helm_chart

    def dump(self):
        '''
        This method is used to dump a chart object as a
        serialized string so that we can perform a diff

        It should recurse into dependencies
        '''
        return self.get_helm_chart().SerializeToString()
