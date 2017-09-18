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

from armada.exceptions.base_exception import ArmadaBaseException as ex


class TillerException(ex):
    '''Base class for Tiller exceptions and error handling.'''

    message = 'An unknown Tiller error occured.'


class TillerServicesUnavailableException(TillerException):
    '''Exception for tiller services unavailable.'''

    message = 'Tiller services unavailable.'


class ChartCleanupException(TillerException):
    '''Exception that occures during chart cleanup.'''

    def __init__(self, chart_name):
        message = 'An error occred during cleanup while removing {}'.format(
            chart_name)
        super(ChartCleanupException, self).__init__(message)


class ListChartsException(TillerException):
    '''Exception that occurs when listing charts'''

    message = 'There was an error listing the helm chart releases.'


class PostUpdateJobDeleteException(TillerException):
    '''Exception that occurs when a job deletion'''

    def __init__(self, name, namespace):

        message = 'Failed to delete k8s job {} in {}'.format(
            name, namespace)

        super(PostUpdateJobDeleteException, self).__init__(message)


class PostUpdateJobCreateException(TillerException):
    '''Exception that occurs when a job creation fails.'''

    def __init__(self, name, namespace):

        message = 'Failed to create k8s job {} in {}'.format(
            name, namespace)

        super(PostUpdateJobCreateException, self).__init__(message)


class PreUpdateJobDeleteException(TillerException):
    '''Exception that occurs when a job deletion'''

    def __init__(self, name, namespace):

        message = 'Failed to delete k8s job {} in {}'.format(
            name, namespace)

        super(PreUpdateJobDeleteException, self).__init__(message)


class PreUpdateJobCreateException(TillerException):
    '''Exception that occurs when a job creation fails.'''

    def __init__(self, name, namespace):

        message = 'Failed to create k8s job {} in {}'.format(
            name, namespace)

        super(PreUpdateJobCreateException, self).__init__(message)


class ReleaseException(TillerException):
    '''Exception that occurs when a release fails to install.'''

    def __init__(self, name, status, action):
        til_msg = getattr(status.info, 'Description').encode()
        message = 'Failed to {} release: {} - Tiller Message: {}'.format(
            action, name, til_msg)

        super(ReleaseException, self).__init__(message)


class ChannelException(TillerException):
    '''Exception that occurs during a failed GRPC channel creation'''

    message = 'Failed to create GRPC channel.'


class GetReleaseStatusException(TillerException):
    '''Exception that occurs during a failed Release Testing'''

    def __init__(self, release, version):
        message = 'Failed to get {} status {} version'.format(
            release, version)

        super(GetReleaseStatusException, self).__init__(message)


class GetReleaseContentException(TillerException):
    '''Exception that occurs during a failed Release Testing'''

    def __init__(self, release, version):
        message = 'Failed to get {} content {} version {}'.format(
            release, version)

        super(GetReleaseContentException, self).__init__(message)


class TillerVersionException(TillerException):
    '''Exception that occurs during a failed Release Testing'''

    message = 'Failed to get Tiller Version'
