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

import grpc
import yaml

from hapi.services.tiller_pb2 import ReleaseServiceStub, ListReleasesRequest, \
    InstallReleaseRequest, UpdateReleaseRequest, UninstallReleaseRequest
from hapi.chart.config_pb2 import Config

from k8s import K8s
from ..const import STATUS_DEPLOYED, STATUS_FAILED

from ..exceptions import tiller_exceptions
from ..utils.release import release_prefix

from oslo_config import cfg
from oslo_log import log as logging

TILLER_PORT = 44134
TILLER_VERSION = b'2.5.0'
TILLER_TIMEOUT = 300
RELEASE_LIMIT = 64

# the standard gRPC max message size is 4MB
# this expansion comes at a performance penalty
# but until proper paging is supported, we need
# to support a larger payload as the current
# limit is exhausted with just 10 releases
MAX_MESSAGE_LENGTH = 429496729

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
DOMAIN = "armada"

logging.setup(CONF, DOMAIN)


class Tiller(object):
    '''
    The Tiller class supports communication and requests to the Tiller Helm
    service over gRPC
    '''

    def __init__(self, tiller_host=None, tiller_port=TILLER_PORT):

        self.tiller_host = tiller_host
        self.tiller_port = tiller_port
        # init k8s connectivity
        self.k8s = K8s()

        # init tiller channel
        self.channel = self.get_channel()

        # init timeout for all requests
        # and assume eventually this will
        # be fed at runtime as an override
        self.timeout = TILLER_TIMEOUT

    @property
    def metadata(self):
        '''
        Return tiller metadata for requests
        '''
        return [(b'x-helm-api-client', TILLER_VERSION)]

    def get_channel(self):
        '''
        Return a tiller channel
        '''
        tiller_ip = self._get_tiller_ip()
        tiller_port = self._get_tiller_port()
        try:
            return grpc.insecure_channel(
                '%s:%s' % (tiller_ip, tiller_port),
                options=[('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                         ('grpc.max_receive_message_length',
                          MAX_MESSAGE_LENGTH)])
        except Exception:
            raise tiller_exceptions.ChannelException()

    def _get_tiller_pod(self):
        '''
        Search all namespaces for a pod beginning with tiller-deploy*
        '''
        for i in self.k8s.get_namespace_pod('kube-system').items:
            # TODO(alanmeadows): this is a bit loose
            if i.metadata.name.startswith('tiller-deploy'):
                return i

    def _get_tiller_ip(self):
        '''
        Returns the tiller pod's IP address by searching all namespaces
        '''
        if self.tiller_host:
            return self.tiller_host
        else:
            pod = self._get_tiller_pod()
            return pod.status.pod_ip

    def _get_tiller_port(self):
        '''Stub method to support arbitrary ports in the future'''
        return TILLER_PORT

    def tiller_status(self):
        '''
        return if tiller exist or not
        '''
        if self._get_tiller_ip():
            return True

        return False

    def list_releases(self):
        '''
        List Helm Releases
        '''
        releases = []
        stub = ReleaseServiceStub(self.channel)
        req = ListReleasesRequest(
            limit=RELEASE_LIMIT,
            status_codes=[STATUS_DEPLOYED, STATUS_FAILED],
            sort_by='LAST_RELEASED',
            sort_order='DESC')
        release_list = stub.ListReleases(
            req, self.timeout, metadata=self.metadata)

        for y in release_list:
            releases.extend(y.releases)

        return releases

    def get_chart_templates(self, template_name, name, release_name, namespace,
                            chart, disable_hooks, values):
        # returns some info

        LOG.info("Template( %s ) : %s ", template_name, name)

        stub = ReleaseServiceStub(self.channel)
        release_request = InstallReleaseRequest(
            chart=chart,
            dry_run=True,
            values=values,
            name=name,
            namespace=namespace,
            wait=False)

        templates = stub.InstallRelease(
            release_request, self.timeout, metadata=self.metadata)

        for template in yaml.load_all(
                getattr(templates.release, 'manifest', [])):
            if template_name == template.get('metadata', None).get(
                    'name', None):
                LOG.info(template_name)
                return template

    def _pre_update_actions(self, actions, release_name, namespace, chart,
                            disable_hooks, values):
        '''
        :params actions - array of items actions
        :params namespace - name of pod for actions
        '''

        try:
            for action in actions.get('update', []):
                name = action.get('name')
                LOG.info('Updating %s ', name)
                action_type = action.get('type')
                labels = action.get('labels')

                self.rolling_upgrade_pod_deployment(
                    name, release_name, namespace, labels, action_type, chart,
                    disable_hooks, values)
        except Exception:
            LOG.debug("Pre: Could not update anything, please check yaml")

        try:
            for action in actions.get('delete', []):
                name = action.get('name')
                action_type = action.get('type')
                labels = action.get('labels', None)

                self.delete_resources(release_name, name, action_type, labels,
                                      namespace)

                # Ensure pods get deleted when job is deleted
                if 'job' in action_type:
                    self.delete_resources(release_name, name, 'pod', labels,
                                          namespace)
        except Exception:
            raise tiller_exceptions.PreUpdateJobDeleteException(
                name, namespace)
            LOG.debug("PRE: Could not delete anything, please check yaml")

        try:
            for action in actions.get('create', []):
                name = action.get("name")
                action_type = action.get("type")
                if "job" in action_type:
                    LOG.info("Creating %s in namespace: %s", name, namespace)
                    self.k8s.create_job_action(name, action_type)
                    continue
        except Exception:
            raise tiller_exceptions.PreUpdateJobCreateException(
                name, namespace)
            LOG.debug("PRE: Could not create anything, please check yaml")

    def delete_resource(self, release_name, resource_name, resource_type,
                        resource_labels, namespace):
        '''
        :params release_name - release name the specified resource is under
        :params resource_name - name of specific resource
        :params resource_type - type of resource e.g. job, pod, etc.
        :params resource_labels - labels by which to identify the resource
        :params namespace - namespace of the resource

        Apply deletion logic based on type of resource
        '''

        label_selector = 'release_name={}'.format(release_name)
        for label in resource_labels:
            label_selector += ', {}={}'.format(label.keys()[0],
                                               label.values()[0])

        if 'job' in resource_type:
            LOG.info("Deleting %s in namespace: %s", resource_name, namespace)
            self.k8s.delete_job_action(resource_name, namespace)
        elif 'pod' in resource_type:
            release_pods = self.k8s.get_namespace_pod(namespace,
                                                      label_selector)
            for pod in release_pods.items:
                pod_name = pod.metadata.name
                LOG.info("Deleting %s in namespace: %s", pod_name, namespace)
                self.k8s.delete_namespace_pod(pod_name, namespace)
                self.k8s.wait_for_pod_redeployment(pod_name, namespace)
        else:
            LOG.error("Unable to execute name: %s type: %s ", resource_name,
                      resource_type)

    def _post_update_actions(self, actions, namespace):
        try:
            for action in actions.get('create', []):
                name = action.get("name")
                action_type = action.get("type")
                if "job" in action_type:
                    LOG.info("Creating %s in namespace: %s", name, namespace)
                    self.k8s.create_job_action(name, action_type)
                    continue
        except Exception:
            raise tiller_exceptions.PreUpdateJobCreateException()
            LOG.debug("POST: Could not create anything, please check yaml")

    def list_charts(self):
        '''
        List Helm Charts from Latest Releases

        Returns a list of tuples in the form:
        (name, version, chart, values, status)
        '''
        charts = []
        for latest_release in self.list_releases():
            try:
                charts.append((latest_release.name, latest_release.version,
                               latest_release.chart, latest_release.config.raw,
                               latest_release.info.status.Code.Name(
                                   latest_release.info.status.code)))
            except IndexError:
                continue
        return charts

    def update_release(self,
                       chart,
                       release,
                       namespace,
                       dry_run=False,
                       pre_actions=None,
                       post_actions=None,
                       disable_hooks=False,
                       values=None,
                       wait=False,
                       timeout=None):
        '''
        Update a Helm Release
        '''
        LOG.debug("wait: %s", wait)
        LOG.debug("timeout: %s", timeout)

        if values is None:
            values = Config(raw='')
        else:
            values = Config(raw=values)

        self._pre_update_actions(pre_actions, release, namespace, chart,
                                 disable_hooks, values)

        # build release install request
        try:
            stub = ReleaseServiceStub(self.channel)
            release_request = UpdateReleaseRequest(
                chart=chart,
                dry_run=dry_run,
                disable_hooks=disable_hooks,
                values=values,
                name=release,
                wait=wait,
                timeout=timeout)

            stub.UpdateRelease(
                release_request, self.timeout, metadata=self.metadata)
        except Exception:
            raise tiller_exceptions.ReleaseInstallException(release, namespace)

        self._post_update_actions(post_actions, namespace)

    def install_release(self,
                        chart,
                        release,
                        namespace,
                        dry_run=False,
                        values=None,
                        wait=False,
                        timeout=None):
        '''
        Create a Helm Release
        '''
        LOG.debug("wait: %s", wait)
        LOG.debug("timeout: %s", timeout)

        if values is None:
            values = Config(raw='')
        else:
            values = Config(raw=values)

        # build release install request
        try:
            stub = ReleaseServiceStub(self.channel)
            release_request = InstallReleaseRequest(
                chart=chart,
                dry_run=dry_run,
                values=values,
                name=release,
                namespace=namespace,
                wait=wait,
                timeout=timeout)

            return stub.InstallRelease(
                release_request, self.timeout, metadata=self.metadata)

        except Exception:
            raise tiller_exceptions.ReleaseInstallException(release, namespace)

    def uninstall_release(self, release, disable_hooks=False, purge=True):
        '''
        :params - release - helm chart release name
        :params - purge - deep delete of chart

        deletes a helm chart from tiller
        '''

        # build release install request
        try:
            stub = ReleaseServiceStub(self.channel)
            release_request = UninstallReleaseRequest(
                name=release, disable_hooks=disable_hooks, purge=purge)

            return stub.UninstallRelease(
                release_request, self.timeout, metadata=self.metadata)

        except Exception:
            raise tiller_exceptions.ReleaseUninstallException(release)

    def chart_cleanup(self, prefix, charts):
        '''
        :params charts - list of yaml charts
        :params known_release - list of releases in tiller

        :result - will remove any chart that is not present in yaml
        '''

        valid_charts = []
        for gchart in charts:
            for chart in gchart.get('chart_group'):
                valid_charts.append(
                    release_prefix(prefix, chart.get('chart').get('name')))

        actual_charts = [x.name for x in self.list_releases()]
        chart_diff = list(set(actual_charts) - set(valid_charts))

        for chart in chart_diff:
            if chart.startswith(prefix):
                LOG.debug("Release: %s will be removed", chart)
                self.uninstall_release(chart)

    def delete_resources(self, release_name, resource_name, resource_type,
                         resource_labels, namespace):
        '''
        :params release_name - release name the specified resource is under
        :params resource_name - name of specific resource
        :params resource_type - type of resource e.g. job, pod, etc.
        :params resource_labels - labels by which to identify the resource
        :params namespace - namespace of the resource

        Apply deletion logic based on type of resource
        '''

        label_selector = ''

        if not resource_type == 'job':
            label_selector = 'release_name={}'.format(release_name)

        if resource_labels is not None:
            for label in resource_labels:
                if label_selector == '':
                    label_selector = '{}={}'.format(label.keys()[0],
                                                    label.values()[0])
                    continue

                label_selector += ', {}={}'.format(label.keys()[0],
                                                   label.values()[0])

        if 'job' in resource_type:
            LOG.info("Deleting %s in namespace: %s", resource_name, namespace)
            get_jobs = self.k8s.get_namespace_job(namespace, label_selector)
            for jb in get_jobs.items:
                jb_name = jb.metadata.name

                self.k8s.delete_job_action(jb_name, namespace)

        elif 'pod' in resource_type:
            release_pods = self.k8s.get_namespace_pod(namespace,
                                                      label_selector)

            for pod in release_pods.items:
                pod_name = pod.metadata.name
                LOG.info("Deleting %s in namespace: %s", pod_name, namespace)
                self.k8s.delete_namespace_pod(pod_name, namespace)
                self.k8s.wait_for_pod_redeployment(pod_name, namespace)
        else:
            LOG.error("Unable to execute name: %s type: %s ", resource_name,
                      resource_type)

    def rolling_upgrade_pod_deployment(self, name, release_name, namespace,
                                       labels, action_type, chart,
                                       disable_hooks, values):
        '''
        update statefullsets (daemon, stateful)
        '''

        if action_type == 'daemonset':

            LOG.info('Updating: %s', action_type)
            label_selector = 'release_name={}'.format(release_name)

            if labels is not None:
                for label in labels:
                    label_selector += ', {}={}'.format(label.keys()[0],
                                                       label.values()[0])

            get_daemonset = self.k8s.get_namespace_daemonset(
                namespace=namespace, label=label_selector)

            for ds in get_daemonset.items:
                ds_name = ds.metadata.name
                ds_labels = ds.metadata.labels
                if ds_name == name:
                    LOG.info("Deleting %s : %s in %s", action_type, ds_name,
                             namespace)
                    self.k8s.delete_daemon_action(ds_name, namespace)

                    # update the daemonset yaml
                    template = self.get_chart_templates(
                        ds_name, name, release_name, namespace, chart,
                        disable_hooks, values)
                    template['metadata']['labels'] = ds_labels
                    template['spec']['template']['metadata'][
                        'labels'] = ds_labels

                    self.k8s.create_daemon_action(
                        namespace=namespace, template=template)

                    # delete pods
                    self.delete_resources(release_name, name, 'pod', labels,
                                          namespace)

        elif action_type == 'statefulset':
            pass
