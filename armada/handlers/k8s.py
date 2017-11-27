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
import time

from kubernetes import client
from kubernetes import config
from kubernetes import watch
from kubernetes.client.rest import ApiException
from oslo_config import cfg
from oslo_log import log as logging

from armada.utils.release import label_selectors


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
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()

        self.client = client.CoreV1Api()
        self.batch_api = client.BatchV1Api()
        self.extension_api = client.ExtensionsV1beta1Api()

    def delete_job_action(self, name, namespace="default",
                          propagation_policy='Foreground'):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        :params propagation_policy - The Kubernetes propagation_policy to apply
                                    to the delete. Default 'Foreground' means
                                    that child Pods to the Job will be deleted
                                    before the Job is marked as deleted.
        '''
        try:
            body = client.V1DeleteOptions()
            self.batch_api.delete_namespaced_job(
                name=name, namespace=namespace, body=body,
                propagation_policy=propagation_policy)
        except ApiException as e:
            LOG.error("Exception when deleting a job: %s", e)

    def get_namespace_job(self, namespace="default", label_selector=''):
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

    def get_namespace_pod(self, namespace="default", label_selector=''):
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

        return self.client.delete_namespaced_pod(name, namespace, body)

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
                    if (condition.type == 'Ready' and
                            condition.status == 'True'):
                        LOG.info('New pod %s deployed', new_pod_name)
                        w.stop()

    def wait_get_running_podphase(self, release, timeout=300):
        '''
        :param release - part of namespace
        :param timeout - time before disconnecting stream
        '''

        w = watch.Watch()
        for event in w.stream(self.client.list_pod_for_all_namespaces,
                              timeout_seconds=timeout):
            pod_name = event['object'].metadata.name

            if release in pod_name:
                pod_state = event['object'].status.phase
                if pod_state == 'Running':
                    w.stop()
                    break

    def wait_until_ready(self,
                         release=None,
                         namespace='default',
                         labels='',
                         timeout=300,
                         sleep=15):
        '''
        :param release - part of namespace
        :param timeout - time before disconnecting stream
        '''
        LOG.debug("Wait on %s for %s sec", namespace, timeout)

        label_selector = ''

        if labels:
            label_selector = label_selectors(labels)

        valid_state = ['Succeeded', 'Running']

        wait_timeout = time.time() + 60 * timeout

        while True:

            self.is_pods_ready(label_selector=label_selector, timeout=timeout)

            pod_ready = []
            not_ready = []
            for pod in self.client.list_pod_for_all_namespaces(
                    label_selector=label_selector).items:
                p_state = pod.status.phase
                p_name = pod.metadata.name
                if p_state in valid_state:
                    pod_ready.append(True)
                    continue

                pod_ready.append(False)
                not_ready.append(p_name)

                LOG.debug('%s', p_state)

            if time.time() > wait_timeout or all(pod_ready):
                LOG.debug("Pod States %s", pod_ready)
                break
            if time.time() > wait_timeout and not all(pod_ready):
                LOG.exception(
                    'Failed to bring up release %s: %s', release, not_ready)
                break
            else:
                LOG.debug('time: %s pod %s', wait_timeout, pod_ready)

    def is_pods_ready(self, label_selector='', timeout=100):
        '''
        :params release_labels - list of labels to identify relevant pods
        :params namespace - namespace in which to search for pods

        Returns after waiting for all pods to enter Ready state
        '''
        pods_found = []
        valid_state = ['Succeeded', 'Running']

        w = watch.Watch()
        for pod in w.stream(self.client.list_pod_for_all_namespaces,
                            label_selector=label_selector,
                            timeout_seconds=timeout):

            pod_name = pod['object'].metadata.name
            pod_state = pod['object'].status.phase

            if pod['type'] == 'ADDED' and pod_state not in valid_state:
                LOG.debug("Pod %s in %s", pod_name, pod_state)
                pods_found.append(pod_name)
            elif pod_name in pods_found:
                if pod_state in valid_state:
                    pods_found.remove(pod_name)
                    LOG.debug(pods_found)

            if not pods_found:
                LOG.debug('Terminate wait')
                w.stop()

    def get_test_pod_log(self, release, follow=False, label_selector=''):
        '''
        :param release: pod release
        :param follow: watch pod
        :param label: pod label
        '''

        pods = self.get_all_pods(label_selector=label_selector)
        for pod in pods.items:
            p_name = pod.metadata.name
            p_namespace = pod.metadata.namespace

            if release in p_name:
                return self.client.read_namespaced_pod_log(
                    p_name, p_namespace, follow=follow)

    def find_pod(self, name, label_selector=''):
        pods = self.get_all_pods(label_selector=label_selector)

        for pod in pods.items:
            p_name = pod.metadata.name

            if p_name == name:
                return True

        return False
