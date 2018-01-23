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

from oslo_log import log as logging

from armada import const
from armada import exceptions

LOG = logging.getLogger(__name__)


class Manifest(object):

    def __init__(self, documents, target_manifest=None):
        """Instantiates a Manifest object.

        An Armada Manifest expects that at least one of each of the following
        be included in ``documents``:

        * A document with schema "armada/Chart/v1"
        * A document with schema "armada/ChartGroup/v1"

        And only one document of the following is allowed:

        * A document with schema "armada/Manifest/v1"

        If multiple documents with schema "armada/Manifest/v1" are provided,
        specify ``target_manifest`` to select the target one.

        :param List[dict] documents: Documents out of which to build the
            Armada Manifest.
        :param str target_manifest: The target manifest to use when multiple
            documents with "armada/Manifest/v1" are contained in
            ``documents``. Default is None.
        :raises ManifestException: If the expected number of document types
            are not found or if the document types are missing required
            properties.
        """
        self.config = None
        self.documents = documents
        self.charts, self.groups, manifests = self._find_documents(
            target_manifest)

        if len(manifests) > 1:
            error = ('Multiple manifests are not supported. Ensure that the '
                     '`target_manifest` option is set to specify the target '
                     'manifest')
            LOG.error(error)
            raise exceptions.ManifestException(details=error)
        else:
            self.manifest = manifests[0] if manifests else None

        if not all([self.charts, self.groups, self.manifest]):
            expected_schemas = [const.DOCUMENT_CHART, const.DOCUMENT_GROUP]
            error = ('Documents must be a list of documents with at least one '
                     'of each of the following schemas: %s and only one '
                     'manifest' % expected_schemas)
            LOG.error(error, expected_schemas)
            raise exceptions.ManifestException(
                details=error % expected_schemas)

    def _find_documents(self, target_manifest=None):
        charts = []
        groups = []
        manifests = []
        for document in self.documents:
            if document.get('schema') == const.DOCUMENT_CHART:
                charts.append(document)
            if document.get('schema') == const.DOCUMENT_GROUP:
                groups.append(document)
            if document.get('schema') == const.DOCUMENT_MANIFEST:
                manifest_name = document.get('metadata', {}).get('name')
                if target_manifest:
                    if manifest_name == target_manifest:
                        manifests.append(document)
                else:
                    manifests.append(document)
        return charts, groups, manifests

    def find_chart_document(self, name):
        for chart in self.charts:
            if chart.get('metadata', {}).get('name') == name:
                return chart
        raise exceptions.ManifestException(
            details='Could not find a {} named "{}"'.format(
                const.DOCUMENT_CHART, name))

    def find_chart_group_document(self, name):
        for group in self.groups:
            if group.get('metadata', {}).get('name') == name:
                return group
        raise exceptions.ManifestException(
            details='Could not find a {} named "{}"'.format(
                const.DOCUMENT_GROUP, name))

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
            raise exceptions.ManifestException(
                details="Could not find dependency chart {} in {}".format(
                    dep, const.DOCUMENT_CHART))

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
            raise exceptions.ManifestException(
                details="Could not find chart {} in {}".format(
                    chart, const.DOCUMENT_GROUP))

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
            raise exceptions.ManifestException(
                "Could not find chart group {} in {}".format(
                    group, const.DOCUMENT_MANIFEST))

    def get_manifest(self):
        self.build_charts_deps()
        self.build_chart_groups()
        self.build_armada_manifest()

        return {
            'armada': self.manifest.get('data')
        }
