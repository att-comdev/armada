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

from ..const import DOCUMENT_CHART, DOCUMENT_GROUP, DOCUMENT_MANIFEST

class Manifest(object):
    def __init__(self, documents):
        self.config = None
        self.documents = documents
        self.charts = []
        self.groups = []
        self.manifest = None
        self.get_documents()

    def get_documents(self):
        for document in self.documents:
            if document.get('schema') == DOCUMENT_CHART:
                self.charts.append(document)
            if document.get('schema') == DOCUMENT_GROUP:
                self.groups.append(document)
            if document.get('schema') == DOCUMENT_MANIFEST:
                self.manifest = document

    def find_chart_document(self, name):
        try:
            for chart in self.charts:
                if chart.get('metadata').get('name') == name:
                    return chart
        except Exception:
            raise Exception(
                "Could not find {} in {}".format(name, DOCUMENT_CHART))

    def find_chart_group_document(self, name):
        try:
            for group in self.groups:
                if group.get('metadata').get('name') == name:
                    return group
        except Exception:
            raise Exception(
                "Could not find {} in {}".format(name, DOCUMENT_GROUP))

    def build_charts_deps(self):
        for chart in self.charts:
            self.build_chart_deps(chart)

    def build_chart_groups(self):
        for chart_group in self.groups:
            self.build_chart_group(chart_group)

    def build_chart_deps(self, chart):
        try:
            dep = None
            for iter, dep in enumerate(chart.get('data').get('dependencies')):
                if isinstance(dep, dict):
                    continue
                chart_dep = self.find_chart_document(dep)
                self.build_chart_deps(chart_dep)
                chart['data']['dependencies'][iter] = {
                    'chart': chart_dep.get('data')
                }
        except Exception:
            raise Exception(
                "Could not find dependency chart {} in {}".format(
                    dep, DOCUMENT_CHART))

    def build_chart_group(self, chart_group):
        try:
            chart = None
            for iter, chart in enumerate(chart_group.get('data').get(
                    'chart_group', [])):
                if isinstance(chart, dict):
                    continue
                chart_dep = self.find_chart_document(chart)
                chart_group['data']['chart_group'][iter] = {
                    'chart': chart_dep.get('data')
                }
        except Exception:
            raise Exception(
                "Could not find chart {} in {}".format(
                    chart, DOCUMENT_GROUP))

    def build_armada_manifest(self):
        try:
            group = None
            for iter, group in enumerate(self.manifest.get('data').get(
                    'chart_groups', [])):
                if isinstance(group, dict):
                    continue
                chart_grp = self.find_chart_group_document(group)

                # Add name to chart group
                ch_grp_data = chart_grp.get('data')
                ch_grp_data['name'] = chart_grp.get('metadata').get('name')

                self.manifest['data']['chart_groups'][iter] = ch_grp_data
        except Exception:
            raise Exception(
                "Could not find chart group {} in {}".format(
                    group, DOCUMENT_MANIFEST))

    def get_manifest(self):
        self.build_charts_deps()
        self.build_chart_groups()
        self.build_armada_manifest()

        return {
            'armada': self.manifest.get('data')
        }
