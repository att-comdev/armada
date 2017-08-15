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

import re
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

CONF = cfg.CONF


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
        self.batch_api = client.BatchV1Api()
        self.extension_api = client.ExtensionsV1beta1Api()

    def delete_job_action(self, name, namespace="default"):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        '''
        try:
            body = client.V1DeleteOptions()
            self.batch_api.delete_namespaced_job(
                name=name, namespace=namespace, body=body)
        except ApiException as e:
            LOG.error("Exception when deleting a job: %s", e)

    def get_namespace_job(self, namespace="default",
                          label_selector=''):
        '''
        :params lables - of the job
        :params namespace - name of jobs
        '''

        try:
            return self.batch_api.list_namespaced_job(
                namespace, label_selector=label_selector)
        except ApiException as e:
            LOG.error("Exception getting a job: %s", e)

    def create_job_action(self, name, namespace="default"):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        '''
        LOG.debug(" %s in namespace: %s", name, namespace)

    def get_namespace_pod(self, namespace="default",
                          label_selector=''):
        '''
        :params namespace - namespace of the Pod
        :params label_selector - filters Pods by label

        This will return a list of objects req namespace
        '''

        return self.client.list_namespaced_pod(
            namespace, label_selector=label_selector)

    def get_all_pods(self, label_selector=''):
        '''
        :params label_selector - filters Pods by label

        Returns a list of pods from all namespaces
        '''

        return self.client.list_pod_for_all_namespaces(
            label_selector=label_selector)

    def get_namespace_daemonset(self, namespace='default', label=''):
        '''
        :param namespace - namespace of target deamonset
        :param labels - specify targeted daemonset
        '''
        return self.extension_api.list_namespaced_daemon_set(
            namespace, label_selector=label)

    def create_daemon_action(self, namespace, template):
        '''
        :param - namespace - pod namespace
        :param - template - deploy daemonset via yaml
        '''
        # we might need to load something here

        self.extension_api.create_namespaced_daemon_set(
            namespace, body=template)

    def delete_daemon_action(self, name, namespace="default", body=None):
        '''
        :params - namespace - pod namespace

        This will delete daemonset
        '''

        if body is None:
            body = client.V1DeleteOptions()

        return self.extension_api.delete_namespaced_daemon_set(
            name, namespace, body)

    def delete_namespace_pod(self, name, namespace="default", body=None):
        '''
        :params name - name of the Pod
        :params namespace - namespace of the Pod
        :params body - V1DeleteOptions

        Deletes pod by name and returns V1Status object
        '''
        if body is None:
            body = client.V1DeleteOptions()

        return self.client.delete_namespaced_pod(
            name, namespace, body)

    def wait_for_pod_redeployment(self, old_pod_name, namespace):
        '''
        :param old_pod_name - name of pods
        :param namespace - kubernetes namespace
        '''

        base_pod_pattern = re.compile('^(.+)-[a-zA-Z0-9]+$')

        if not base_pod_pattern.match(old_pod_name):
            LOG.error('Could not identify new pod after purging %s',
                      old_pod_name)
            return

        pod_base_name = base_pod_pattern.match(old_pod_name).group(1)

        new_pod_name = ''

        w = watch.Watch()
        for event in w.stream(self.client.list_namespaced_pod, namespace):
            event_name = event['object'].metadata.name
            event_match = base_pod_pattern.match(event_name)
            if not event_match or not event_match.group(1) == pod_base_name:
                continue

            pod_conditions = event['object'].status.conditions
            # wait for new pod deployment
            if event['type'] == 'ADDED' and not pod_conditions:
                new_pod_name = event_name
            elif new_pod_name:
                for condition in pod_conditions:
                    if (condition.type == 'Ready'
                            and condition.status == 'True'):
                        LOG.info('New pod %s deployed', new_pod_name)

                        w.stop()

    def wait_for_all_pods_ready(self, release_names, namespace):
        '''
        :params release_names - list of prefixes of expected pods
        :params namespace - namespace of releases in which to search for pods

        Note: in order to wait for all pods of multiple releases in more than
              one namespace, this method must be called separately for each
              namespace

        Returns after waiting for all pods to enter Ready state
        '''
        base_pod_pattern = re.compile('^([a-zA-Z0-9]+)-.+$')
        first_pod_deployed = False
        pods_found = []

        w = watch.Watch()
        for pod in w.stream(self.client.list_namespaced_pod, namespace):
            pod_name = pod['object'].metadata.name
            release_match = base_pod_pattern.match(pod_name)
            if not release_match or not release_match.group(1) in release_names:
                continue

            # found a relevant pod
            #
            # ASSUMES PODS WILL ALL BE CREATED BEFORE ANY BECOME READY - TEST
            pod_conditions = pod['object'].status.conditions
            if pod['type'] == 'ADDED':
                pods_found.append(pod_name)
            elif pod_name in pods_found:
                for condition in pod_conditions:
                    if (condition.type == 'Ready'
                            and condition.status == 'True'):
                        LOG.debug('Pod %s deployed', pod_name)
                        pods_found.remove(pod_name)
                        if not first_pod_deployed:
                            first_pod_deployed = True

            if first_pod_deployed and not pods_found:
                w.stop()
