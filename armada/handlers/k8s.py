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

from armada.const import DEFAULT_K8S_TIMEOUT
from armada.utils.release import label_selectors
from armada.exceptions import k8s_exceptions as exceptions

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


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
                          propagation_policy='Foreground',
                          timeout=DEFAULT_K8S_TIMEOUT):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        :params propagation_policy - The Kubernetes propagation_policy to apply
                                    to the delete. Default 'Foreground' means
                                    that child Pods to the Job will be deleted
                                    before the Job is marked as deleted.
        '''
        try:
            LOG.debug('Deleting job %s, Wait timeout=%s', name, timeout)
            body = client.V1DeleteOptions()
            w = watch.Watch()
            issue_delete = True
            for event in w.stream(self.batch_api.list_namespaced_job,
                                  namespace=namespace,
                                  timeout_seconds=timeout):
                if issue_delete:
                    self.batch_api.delete_namespaced_job(
                        name=name, namespace=namespace, body=body,
                        propagation_policy=propagation_policy)
                    issue_delete = False

                event_type = event['type'].upper()
                job_name = event['object'].metadata.name

                if event_type == 'DELETED' and job_name == name:
                    LOG.debug('Successfully deleted job %s', job_name)
                    return

            LOG.info(
                'Reached timeout while waiting to delete job %s, namespace=%s',
                name, namespace)
            raise exceptions.KubernetesWatchTimeoutException(
                'Timed out while deleting job: name=%s, namespace=%s' %
                (name, namespace))

        except ApiException as e:
            LOG.exception(
                "Exception when deleting job: name=%s, namespace=%s",
                name, namespace)
            raise e

    def get_namespace_job(self, namespace="default", label_selector=''):
        '''
        :params lables - of the job
        :params namespace - name of jobs
        '''

        try:
            return self.batch_api.list_namespaced_job(
                namespace, label_selector=label_selector)
        except ApiException as e:
            LOG.error("Exception getting a job: namespace=%s, label=%s: %s",
                      namespace, label_selector, e)

    def create_job_action(self, name, namespace="default"):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        '''
        # TODO(MarshM) this does nothing?
        LOG.debug(" %s in namespace: %s", name, namespace)

    def get_namespace_pod(self, namespace="default", label_selector=''):
        '''
        :params namespace - namespace of the Pod
        :params label_selector - filters Pods by label

        This will return a list of objects req namespace
        '''

        return self.client.list_namespaced_pod(
            namespace, label_selector=label_selector)

    # TODO(MarshM) unused?
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

    def wait_get_completed_podphase(self, release,
                                    timeout=DEFAULT_K8S_TIMEOUT):
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
                if pod_state == 'Succeeded':
                    w.stop()
                    break

    def wait_until_ready(self,
                         release=None,
                         namespace='',
                         labels='',
                         timeout=DEFAULT_K8S_TIMEOUT,
                         k8s_wait_attempts=1,
                         k8s_wait_attempt_sleep=1):
        '''
        Wait until all pods become ready given the filters provided by
        ``release``, ``labels`` and ``namespace``.

        :param release: chart release
        :param namespace: the namespace used to filter which pods to wait on
        :param labels: the labels used to filter which pods to wait on
        :param timeout: time before disconnecting ``Watch`` stream
        :param k8s_wait_attempts: The number of times to attempt waiting
            for pods to become ready (minimum 1).
        :param k8s_wait_attempt_sleep: The time in seconds to sleep
            between attempts (minimum 1).
        '''
        # NOTE(MarshM) 'release' is currently unused
        label_selector = label_selectors(labels) if labels else ''

        wait_attempts = (k8s_wait_attempts if k8s_wait_attempts >= 1 else 1)
        sleep_time = (k8s_wait_attempt_sleep if k8s_wait_attempt_sleep >= 1
                      else 1)

        LOG.debug("Wait on namespace=(%s) labels=(%s) for %s sec "
                  "(k8s wait %s times, sleep %ss)",
                  namespace, label_selector, timeout,
                  wait_attempts, sleep_time)

        if not namespace:
            # This shouldn't be reachable
            LOG.warn('"namespace" not specified, waiting across all available '
                     'namespaces is likely to cause unintended consequences.')
        if not label_selector:
            LOG.warn('"label_selector" not specified, waiting with no labels '
                     'may cause unintended consequences.')

        deadline = time.time() + timeout

        # NOTE(mark-burnett): Attempt to wait multiple times without
        # modification, in case new pods appear after our watch exits.

        successes = 0
        while successes < wait_attempts:
            deadline_remaining = int(round(deadline - time.time()))
            if deadline_remaining <= 0:
                return False
            timed_out, modified_pods, unready_pods = self._wait_one_time(
                namespace=namespace, label_selector=label_selector,
                timeout=deadline_remaining)

            if timed_out:
                LOG.info('Timed out waiting for pods: %s',
                         sorted(unready_pods))
                raise exceptions.KubernetesWatchTimeoutException(
                    'Timed out while waiting on namespace=(%s) labels=(%s)' %
                    (namespace, label_selector))
                return False

            if modified_pods:
                successes = 0
                LOG.debug('Continuing to wait, found modified pods: %s',
                          sorted(modified_pods))
            else:
                successes += 1
                LOG.debug('Found no modified pods this attempt. successes=%d',
                          successes)

            time.sleep(sleep_time)

        return True

    def _wait_one_time(self, namespace, label_selector, timeout=100):
        LOG.debug('Starting to wait: namespace=%s, label_selector=%s, '
                  'timeout=%s', namespace, label_selector, timeout)
        ready_pods = {}
        modified_pods = set()
        w = watch.Watch()
        first_event = True

        # Watch across specific namespace, or all
        kwargs = {
            'label_selector': label_selector,
            'timeout_seconds': timeout,
        }
        if namespace:
            func_to_call = self.client.list_namespaced_pod
            kwargs['namespace'] = namespace
        else:
            func_to_call = self.client.list_pod_for_all_namespaces

        for event in w.stream(func_to_call, **kwargs):
            if first_event:
                pod_list = func_to_call(**kwargs)
                for pod in pod_list.items:
                    LOG.debug('Setting up to wait for pod %s namespace=%s',
                              pod.metadata.name, pod.metadata.namespace)
                    ready_pods[pod.metadata.name] = False
                first_event = False

            event_type = event['type'].upper()
            pod_name = event['object'].metadata.name
            LOG.debug('Watch event for pod %s namespace=%s label_selector=%s',
                      pod_name, namespace, label_selector)

            if event_type in {'ADDED', 'MODIFIED'}:
                status = event['object'].status
                pod_phase = status.phase

                pod_ready = True
                if (pod_phase == 'Succeeded' or
                    (pod_phase == 'Running' and
                        self._get_pod_condition(status.conditions,
                                                'Ready') == 'True')):
                    LOG.debug('Pod %s is ready!', pod_name)
                else:
                    pod_ready = False
                    LOG.debug('Pod %s not ready: conditions:\n%s\n'
                              'container_statuses:\n%s', pod_name,
                              status.conditions, status.container_statuses)

                ready_pods[pod_name] = pod_ready

                if event_type == 'MODIFIED':
                    modified_pods.add(pod_name)

            elif event_type == 'DELETED':
                LOG.debug('Pod %s: removed from tracking', pod_name)
                ready_pods.pop(pod_name)

            elif event_type == 'ERROR':
                LOG.error('Pod %s: Got error event %s',
                          pod_name, event['object'].to_dict())
                raise exceptions.KubernetesErrorEventException(
                    'Got error event for pod: %s' % event['object'])

            else:
                LOG.error('Unrecognized event type (%s) for pod: %s',
                          event_type, event['object'])
                raise exceptions.KubernetesUnknownStreamingEventTypeException(
                    'Got unknown event type (%s) for pod: %s'
                    % (event_type, event['object']))

            if all(ready_pods.values()):
                return (False, modified_pods, [])

        # NOTE(mark-burnett): This path is reachable if there are no pods
        # (unlikely) or in the case of the watch timing out.
        return (not all(ready_pods.values()), modified_pods,
                [name for name, ready in ready_pods.items() if not ready])

    def _get_pod_condition(self, pod_conditions, condition_type):
        for pc in pod_conditions:
            if pc.type == condition_type:
                return pc.status
