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

from armada.exceptions import base_exception


class ChartBuilderException(base_exception.ArmadaBaseException):
    '''Base class for the Chartbuilder handler exception and error handling.'''

    message = 'An unknown Armada handler error occurred.'


class DependencyException(ChartBuilderException):
    '''
    Exception that occurs when dependencies cannot be resolved.

    **Troubleshoot:**
    *Coming Soon*
    '''

    def __init__(self, chart_name):
        self._chart_name = chart_name
        self._message = 'Failed to resolve dependencies for ' + \
                        self._chart_name + '.'

        super(DependencyException, self).__init__(self._message)


class HelmChartBuildException(ChartBuilderException):
    '''
    Exception that occurs when Helm Chart fails to build.

    **Troubleshoot:**
    *Coming Soon*
    '''

    def __init__(self, chart_name, details):
        self._chart_name = chart_name
        self._message = ('Failed to build Helm chart for %(chart_name)s. '
                         'Details: %(details)s'.format(
                             **{'chart_name': chart_name,
                                'details': details}))

        super(HelmChartBuildException, self).__init__(self._message)


class FilesLoadException(ChartBuilderException):
    '''
    Exception that occurs while trying to read a file in the chart directory.

    **Troubleshoot:**

    * Ensure that the file can be encoded to utf-8 or else it cannot be parsed.
    '''

    message = ('A %(clazz)s exception occurred while trying to read '
               'file: %(file)s. Details:\n%(details)s')


class IgnoredFilesLoadException(ChartBuilderException):
    '''
    Exception that occurs when there is an error loading files contained in
    .helmignore.

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'An error occurred while loading the ignored files in \
              .helmignore'


class MetadataLoadException(ChartBuilderException):
    '''
    Exception that occurs when metadata loading fails.

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'Failed to load metadata from chart yaml file'


class UnknownChartSourceException(ChartBuilderException):
    '''Exception for unknown chart source type.'''

    def __init__(self, chart_name, source_type):
        self._chart_name = chart_name
        self._source_type = source_type

        self._message = 'Unknown source type \"' + self._source_type + '\" for \
                         chart \"' + self._chart_name + '\"'

        super(UnknownChartSourceException, self).__init__(self._message)
