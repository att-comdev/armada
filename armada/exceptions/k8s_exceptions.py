# Copyright 2018 The Armada Authors.
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


class KubernetesException(ex):
    '''Base class for Kubernetes exceptions and error handling.'''

    message = 'An unknown Kubernetes error occurred.'


class KubernetesWatchTimeoutException(KubernetesException):
    '''Exception for timing out during a watch on a Kubernetes object'''

    message = 'Kubernetes Watch has timed out.'


class KubernetesUnknownStreamingEventTypeException(KubernetesException):
    '''Exception for getting an unknown event type from the Kubernetes API'''

    message = 'An unknown event type was returned from the streaming API.'


class KubernetesErrorEventException(KubernetesException):
    '''Exception for getting an error from the Kubernetes API'''

    message = 'An error event was returned from the streaming API.'
