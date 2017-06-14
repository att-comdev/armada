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

from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging

LOG = logging.getLogger(__name__)

class K8s(object):
    '''
    Object to obtain the local kube config file
    '''
    def __init__(self):
        '''
        Initialize connection to Kubernetes
        '''
        config.load_kube_config()
        self.client = client.CoreV1Api()
        self.api_client = client.BatchV1Api()

    def delete_job_action(self, name, namespace="default"):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        '''
        try:
            body = client.V1DeleteOptions()
            self.api_client.delete_namespaced_job(name=name,
                                                  namespace=namespace,
                                                  body=body)
        except ApiException as e:
            LOG.error("Exception when deleting a job: %s", e)

    def create_job_action(self, name, namespace="default"):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        '''
        LOG.debug(" %s in namespace: %s", name, namespace)

    def get_namespace_pod(self, namespace="default"):
        '''
        :params - namespace - pod namespace

        This will return a list of objects req namespace
        '''

        return self.client.list_namespaced_pod(namespace)

    def get_all_pods(self, label_selector=''):
        '''
        :params - label_selector - filters pods by label

        Returns a list of pods from all namespaces
        '''

        return self.client \
            .list_pod_for_all_namespaces(label_selector=label_selector)
