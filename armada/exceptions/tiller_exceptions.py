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
    '''
    Exception for tiller services unavailable.

    **Message:**
    *Tiller services unavailable.*

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'Tiller services unavailable.'


class ChartCleanupException(TillerException):
    '''Exception that occures during chart cleanup.'''

    def __init__(self, chart_name):
        message = 'An error occurred during cleanup while removing {}'.format(
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
    '''
    Exception that occurs when a job creation fails.

    **Message:**
    *Failed to create k8s job <name> in <namespace>*

    **Troubleshoot:**
    *Coming Soon*
    '''

    def __init__(self, name, namespace):

        message = 'Failed to create k8s job {} in {}'.format(
            name, namespace)

        super(PostUpdateJobCreateException, self).__init__(message)


class PreUpdateJobDeleteException(TillerException):
    '''
    Exception that occurs when a job deletion.

    **Message:**
    *Failed to delete k8s job <name> in <namespace>*

    **Troubleshoot:**
    *Coming Soon*
    '''

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
    '''
    Exception that occurs when a release fails to install, upgrade, delete,
    or test.

    **Message:**
    *Failed to <action> release: <name> - Tiller Message: <tiller message>*

    **Possible Actions:**
    *delete, install, test, upgrade*

    **Troubleshoot:**
    *Coming Soon*
    '''

    def __init__(self, name, status, action):
        til_msg = getattr(status.info, 'Description').encode()
        message = 'Failed to {} release: {} - Tiller Message: {}'.format(
            action, name, til_msg)

        super(ReleaseException, self).__init__(message)


class ChannelException(TillerException):
    '''
    Exception that occurs during a failed GRPC channel creation.

    **Message:**
    *Failed to create GRPC channel*

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'Failed to create GRPC channel.'


class GetReleaseStatusException(TillerException):
    '''
    Exception that occurs during a failed Release Testing.

    **Message:**
    *Failed to get <release> status <version>*

    **Troubleshoot:**
    *Coming Soon*
    '''

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


class TillerPodNotFoundException(TillerException):
    '''
    Exception that occurs when a tiller pod cannot be found using the labels
    specified in the Armada config.

    **Message:**
    *Could not find tiller pod with labels "<labels>"*

    **Troubleshoot:**
    *Coming Soon*
    '''

    def __init__(self, labels):
        message = 'Could not find tiller pod with labels "{}"'.format(labels)

        super(TillerPodNotFoundException, self).__init__(message)


class TillerPodNotRunningException(TillerException):
    '''
    Exception that occurs when no tiller pod is found in a running state.

    **Message:**
    *No tiller pods found in running state*

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'No tiller pods found in running state'


class TillerVersionException(TillerException):
    '''
    Exception that occurs during a failed Release Testing

    **Message:**
    *Failed to get Tiller Version*

    **Troubleshoot:**
    *Coming Soon*
    '''

    message = 'Failed to get Tiller Version'
