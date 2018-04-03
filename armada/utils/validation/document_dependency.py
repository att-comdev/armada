# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
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
from armada.utils.validation.validation_rule import ValidationRule

LOG = logging.getLogger(__name__)


class DocumentDependencyValidator(ValidationRule):
    def __init__(self):
        super().__init__('Document Dependency Validation', 'ARMxxx')

    def validate(self, manifest):
        """ Validate that the content of the manifest documents is correct

        :param Manifest manifest: The manifest to validate.
        """
        LOG.debug('Validating and building document dependencies.')

        self.charts = manifest.charts
        self.groups = manifest.groups
        # manifests[0] will be the correct/only manifest at this point, due
        # to other validations
        self.manifest = manifest.manifests[0]

        # continue_running = True

        self.build_charts()
        self.build_chart_groups()
        self.build_armada_manifest()

        return self.manifest

    def find_chart_document(self, name):
        """Returns a chart document with the specified name

        :param str name: name of the desired chart document
        :returns: The requested chart document
        :rtype: dict
        :raises ManifestException: If a chart document with the
            specified name is not found
        """
        for chart in self.charts:
            if chart.get('metadata', {}).get('name') == name:
                return chart
        raise exceptions.ManifestException(
            details='Could not find a {} named "{}"'.format(
                const.DOCUMENT_CHART, name))

    def find_chart_group_document(self, name):
        """Returns a chart group document with the specified name

        :param str name: name of the desired chart group document
        :returns: The requested chart group document
        :rtype: dict
        :raises ManifestException: If a chart
            group document with the specified name is not found
        """
        for group in self.groups:
            if group.get('metadata', {}).get('name') == name:
                return group
        raise exceptions.ManifestException(
            details='Could not find a {} named "{}"'.format(
                const.DOCUMENT_GROUP, name))

    def build_charts(self):
        """Build chart dependencies for every ``chart``.
        """
        for chart in self.charts:
            self.build_chart_deps(chart)

    def build_chart_deps(self, chart):
        """Recursively build chart dependencies for ``chart``.

        :param dict chart: The chart whose dependencies will be recursively
            built.
        """
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
        except Exception as e:
            error_msg = "Could not find dependency chart {} in {}".format(
                dep, const.DOCUMENT_CHART)
            diagnostic = 'Check chart dependencies for %s' % dep
            self.report_error(error_msg, None, diagnostic)
            LOG.info('Chart Validation error: %s, details=%s', error_msg, e)

    def build_chart_groups(self):
        """Build chart dependencies for every ``chart_group``.

        :returns: None
        """
        for chart_group in self.groups:
            self.build_chart_group(chart_group)

    def build_chart_group(self, chart_group):
        """Builds the chart dependencies for`charts`chart group``.

        :param dict chart_group: The chart_group whose dependencies
            will be built.
        """
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
        except Exception as e:
            error_msg = "Could not find chart {} in {}".format(
                chart, const.DOCUMENT_GROUP)
            diagnostic = 'Check chart groups for %s' % chart
            self.report_error(error_msg, None, diagnostic)
            LOG.info('Group Validation error: %s, details=%s', error_msg, e)

    def build_armada_manifest(self):
        """Builds the Armada manifest while pulling out data
        from the chart_group.
        """
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
            error_msg = "Could not find chart group {} in {}".format(
                group, const.DOCUMENT_MANIFEST)
            diagnostic = 'Check chart groups for %s' % group
            self.report_error(error_msg, None, diagnostic)
            LOG.info('Manifest Validation error: %s', error_msg)
