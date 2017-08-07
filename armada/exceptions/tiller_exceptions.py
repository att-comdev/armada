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

import base_exception

class TillerException(base_exception.ArmadaBaseException):
    '''Base class for Tiller exceptions and error handling.'''

    message = 'An unknown Tiller error occured.'

class TillerServicesUnavailableException(TillerException):
    '''Exception for tiller services unavailable.'''

    message = 'Tiller services unavailable.'

class ChartCleanupException(TillerException):
    '''Exception that occures during chart cleanup.'''

    def __init__(self, chart_name, source_type):
        super(ChartCleanupException, self).__init__('An error occred during \
                                                     cleanup while removing \
                                                     the chart ' + chart_name)

class ListChartsException(TillerException):
    '''Exception that occurs when listing charts'''

    message = 'There was an error listing the helm chart releases.'

class PostUpdateJobDeleteException(TillerException):
    '''Exception that occurs when a job deletion'''

    def __init__(self, name, namespace):
        self._name = name
        self._namespace = namespace

        self._message = 'Failed to delete k8s job ' + self._name + ' in ' + \
                        self._namespace + ' namspace.'

        super(PostUpdateJobDeleteException, self).__init__(self._message)

class PostUpdateJobCreateException(TillerException):
    '''Exception that occurs when a job creation fails.'''

    def __init__(self, name, namespace):
        self._name = name
        self._namespace = namespace

        self._message = 'Failed to create k8s job ' + self._name + ' in ' + \
                        self._namespace + ' namespace.'

        super(PostUpdateJobCreateException, self).__init__(self._message)

class PreUpdateJobDeleteException(TillerException):
    '''Exception that occurs when a job deletion'''

    def __init__(self, name, namespace):
        self._name = name
        self._namespace = namespace

        self._message = 'Failed to delete k8s job ' + self._name + ' in ' + \
                        self._namespace + ' namspace.'

        super(PreUpdateJobDeleteException, self).__init__(self._message)

class PreUpdateJobCreateException(TillerException):
    '''Exception that occurs when a job creation fails.'''

    def __init__(self, name, namespace):
        self._name = name
        self._namespace = namespace

        self._message = 'Failed to create k8s job ' + self._name + ' in ' + \
                        self._namespace + ' namespace.'

        super(PreUpdateJobCreateException, self).__init__(self._message)

class ReleaseUninstallException(TillerException):
    '''Exception that occurs when a release fails to uninstall.'''

    def __init__(self, name, namespace):
        self._name = name
        self._message = 'Failed to uninstall release' + self._name + '.'

        super(ReleaseUninstallException, self).__init__(self._message)

class ReleaseInstallException(TillerException):
    '''Exception that occurs when a release fails to install.'''

    def __init__(self, name, namespace):
        self._name = name
        self._message = 'Failed to install release' + self._name + '.'

        super(ReleaseInstallException, self).__init__(self._message)

class ReleaseUpdateException(TillerException):
    '''Exception that occurs when a release fails to update.'''

    def __init__(self, name, namespace):
        self._name = name
        self._message = 'Failed to update release' + self._name + '.'

        super(ReleaseUpdateException, self).__init__(self._message)

class ChannelException(TillerException):
    '''Exception that occurs during a failed GRPC channel creation'''

    message = 'Failed to create GRPC channel.'

class TestingReleaseException(TillerException):
    '''Exception that occurs during a failed Release Testing'''

    def __init__(self, release, exception):
        message = 'Failed run {} tests: {}'
        message.format(release, exception)

        super(TestingReleaseException, self).__init__(self._message)

class GetReleaseStatusException(TillerException):
    '''Exception that occurs during a failed Release Testing'''

    def __init__(self, release, version):
        message = 'Failed to get {} status {} version {}'
        message.format(release, version)

        super(TestingReleaseException, self).__init__(self._message)

class GetReleaseContentException(TillerException):
    '''Exception that occurs during a failed Release Testing'''

    def __init__(self, release, version):
        message = 'Failed to get {} content {} version {}'
        message.format(release, version)

        super(GetReleaseContentException, self).__init__(self._message)

class TillerVersionException(TillerException):
    '''Exception that occurs during a failed Release Testing'''

    message = 'Failed to get Tiller Version'
