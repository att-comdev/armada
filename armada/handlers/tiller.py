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

from hapi.chart.config_pb2 import Config
from hapi.services.tiller_pb2 import GetReleaseContentRequest
from hapi.services.tiller_pb2 import GetReleaseStatusRequest
from hapi.services.tiller_pb2 import GetVersionRequest
from hapi.services.tiller_pb2 import InstallReleaseRequest
from hapi.services.tiller_pb2 import ListReleasesRequest
from hapi.services.tiller_pb2_grpc import ReleaseServiceStub
from hapi.services.tiller_pb2 import TestReleaseRequest
from hapi.services.tiller_pb2 import UninstallReleaseRequest
from hapi.services.tiller_pb2 import UpdateReleaseRequest
from oslo_config import cfg
from oslo_log import log as logging

from armada.const import STATUS_DEPLOYED, STATUS_FAILED
from armada.exceptions import tiller_exceptions as ex
from armada.handlers.k8s import K8s
from armada.utils.release import release_prefix
from armada.utils.release import label_selectors

TILLER_VERSION = b'2.7.2'
TILLER_TIMEOUT = 300
GRPC_EPSILON = 60
RELEASE_LIMIT = 128  # TODO(mark-burnett): There may be a better page size.
RUNTEST_SUCCESS = 9

# the standard gRPC max message size is 4MB
# this expansion comes at a performance penalty
# but until proper paging is supported, we need
# to support a larger payload as the current
# limit is exhausted with just 10 releases
MAX_MESSAGE_LENGTH = 429496729

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class TillerResult(object):
    '''Object to hold Tiller results for Armada.'''
    def __init__(self, release, namespace, status, description, version):
        self.release = release
        self.namespace = namespace
        self.status = status
        self.description = description
        self.version = version


class Tiller(object):
    '''
    The Tiller class supports communication and requests to the Tiller Helm
    service over gRPC
    '''

    def __init__(self, tiller_host=None, tiller_port=None,
                 tiller_namespace=None):
        self.tiller_host = tiller_host
        self.tiller_port = tiller_port or CONF.tiller_port
        self.tiller_namespace = tiller_namespace or CONF.tiller_namespace
        # init k8s connectivity
        self.k8s = K8s()

        # init Tiller channel
        self.channel = self.get_channel()

        # init timeout for all requests
        # and assume eventually this will
        # be fed at runtime as an override
        self.timeout = TILLER_TIMEOUT

        LOG.debug('Armada is using Tiller at: %s:%s, namespace=%s, timeout=%s',
                  self.tiller_host, self.tiller_port, self.tiller_namespace,
                  self.timeout)

    @property
    def metadata(self):
        '''
        Return Tiller metadata for requests
        '''
        return [(b'x-helm-api-client', TILLER_VERSION)]

    def get_channel(self):
        '''
        Return a Tiller channel
        '''
        tiller_ip = self._get_tiller_ip()
        tiller_port = self._get_tiller_port()
        try:
            LOG.debug('Tiller getting gRPC insecure channel at %s:%s '
                      'with options: [grpc.max_send_message_length=%s, '
                      'grpc.max_receive_message_length=%s]',
                      tiller_ip, tiller_port,
                      MAX_MESSAGE_LENGTH, MAX_MESSAGE_LENGTH)
            return grpc.insecure_channel(
                '%s:%s' % (tiller_ip, tiller_port),
                options=[
                    ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                    ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH)
                ]
            )
        except Exception:
            raise ex.ChannelException()

    def _get_tiller_pod(self):
        '''
        Returns Tiller pod using the Tiller pod labels specified in the Armada
        config
        '''
        pods = None
        namespace = self._get_tiller_namespace()
        pods = self.k8s.get_namespace_pod(namespace,
                                          CONF.tiller_pod_labels).items
        # No Tiller pods found
        if not pods:
            raise ex.TillerPodNotFoundException(CONF.tiller_pod_labels)

        # Return first Tiller pod in running state
        for pod in pods:
            if pod.status.phase == 'Running':
                LOG.debug('Found at least one Running Tiller pod.')
                return pod

        # No Tiller pod found in running state
        raise ex.TillerPodNotRunningException()

    def _get_tiller_ip(self):
        '''
        Returns the Tiller pod's IP address by searching all namespaces
        '''
        if self.tiller_host:
            LOG.debug('Using Tiller host IP: %s', self.tiller_host)
            return self.tiller_host
        else:
            pod = self._get_tiller_pod()
            LOG.debug('Using Tiller pod IP: %s', pod.status.pod_ip)
            return pod.status.pod_ip

    def _get_tiller_port(self):
        '''Stub method to support arbitrary ports in the future'''
        LOG.debug('Using Tiller host port: %s', self.tiller_port)
        return self.tiller_port

    def _get_tiller_namespace(self):
        LOG.debug('Using Tiller namespace: %s', self.tiller_namespace)
        return self.tiller_namespace

    def tiller_status(self):
        '''
        return if Tiller exist or not
        '''
        if self._get_tiller_ip():
            LOG.debug('Getting Tiller Status: Tiller exists')
            return True

        LOG.debug('Getting Tiller Status: Tiller does not exist')
        return False

    def list_releases(self):
        '''
        List Helm Releases
        '''
        # TODO(MarshM possibly combine list_releases() with list_charts()
        # since they do the same thing, grouping output differently
        releases = []
        stub = ReleaseServiceStub(self.channel)
        # TODO(mark-burnett): Since we're limiting page size, we need to
        # iterate through all the pages when collecting this list.
        # NOTE(MarshM): `Helm List` defaults to returning Deployed and Failed,
        # but this might not be a desireable ListReleasesRequest default.
        req = ListReleasesRequest(limit=RELEASE_LIMIT,
                                  status_codes=[STATUS_DEPLOYED,
                                                STATUS_FAILED],
                                  sort_by='LAST_RELEASED',
                                  sort_order='DESC')

        LOG.debug('Tiller ListReleases() with timeout=%s', self.timeout)
        release_list = stub.ListReleases(req, self.timeout,
                                         metadata=self.metadata)

        for y in release_list:
            # TODO(MarshM) this log is too noisy, fix later
            # LOG.debug('Found release: %s', y.releases
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
                            disable_hooks, values, timeout):
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
                    name, release_name, namespace, labels,
                    action_type, chart, disable_hooks, values, timeout)
        except Exception:
            LOG.warn("Pre: Could not update anything, please check yaml")
            raise ex.PreUpdateJobDeleteException(name, namespace)

        try:
            for action in actions.get('delete', []):
                name = action.get('name')
                action_type = action.get('type')
                labels = action.get('labels', None)

                self.delete_resources(release_name, name, action_type,
                                      labels, namespace, timeout)
        except Exception:
            LOG.warn("PRE: Could not delete anything, please check yaml")
            raise ex.PreUpdateJobDeleteException(name, namespace)

        try:
            for action in actions.get('create', []):
                name = action.get("name")
                action_type = action.get("type")
                if "job" in action_type:
                    LOG.info("Creating %s in namespace: %s", name, namespace)
                    # TODO(MarshM) create_job_action does nothing but LOG.debug
                    self.k8s.create_job_action(name, action_type)
                    continue
        except Exception:
            LOG.warn("PRE: Could not create anything, please check yaml")
            raise ex.PreUpdateJobCreateException(name, namespace)

    def _post_update_actions(self, actions, namespace):
        try:
            for action in actions.get('create', []):
                name = action.get("name")
                action_type = action.get("type")
                if "job" in action_type:
                    LOG.info("Creating %s in namespace: %s", name, namespace)
                    # TODO(MarshM) create_job_action does nothing but LOG.debug
                    self.k8s.create_job_action(name, action_type)
                    continue
        except Exception:
            LOG.warn("POST: Could not create anything, please check yaml")
            raise ex.PreUpdateJobCreateException(name, namespace)

    def list_charts(self):
        '''
        List Helm Charts from Latest Releases

        Returns a list of tuples in the form:
        (name, version, chart, values, status)
        '''
        LOG.debug('Getting known releases from Tiller...')
        charts = []
        for latest_release in self.list_releases():
            try:
                release = (
                    latest_release.name, latest_release.version,
                    latest_release.chart, latest_release.config.raw,
                    latest_release.info.status.Code.Name(
                        latest_release.info.status.code))
                charts.append(release)
                LOG.debug('Found release %s, version %s, status: %s',
                          release[0], release[1], release[4])
            except (AttributeError, IndexError) as e:
                LOG.debug('%s while getting releases: %s, ex=%s',
                          e.__class__.__name__, latest_release, e)
                continue
        return charts

    def update_release(self, chart, release, namespace,
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

        rel_timeout = self.timeout if not timeout else timeout

        LOG.debug('Helm update release%s: wait=%s, timeout=%s',
                  (' (dry run)' if dry_run else ''),
                  wait, timeout)

        if values is None:
            values = Config(raw='')
        else:
            values = Config(raw=values)

        self._pre_update_actions(pre_actions, release, namespace, chart,
                                 disable_hooks, values, timeout)

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

            update_msg = stub.UpdateRelease(
                release_request, rel_timeout + GRPC_EPSILON,
                metadata=self.metadata)

            tiller_result = TillerResult(
                update_msg.release.name,
                update_msg.release.namespace,
                update_msg.release.info.status.Code.Name(
                    update_msg.release.info.status.code),
                update_msg.release.info.Description,
                update_msg.release.version)

            return tiller_result
        except Exception:
            LOG.exception('Error while updating release %s', release)
            status = self.get_release_status(release)
            raise ex.ReleaseException(release, status, 'Upgrade')

        self._post_update_actions(post_actions, namespace)

    def install_release(self, chart, release, namespace,
                        dry_run=False,
                        values=None,
                        wait=False,
                        timeout=None):
        '''
        Create a Helm Release
        '''

        rel_timeout = self.timeout if not timeout else timeout

        LOG.debug('Helm install release%s: wait=%s, timeout=%s',
                  (' (dry run)' if dry_run else ''),
                  wait, timeout)

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

            install_msg = stub.InstallRelease(
                release_request, rel_timeout + GRPC_EPSILON,
                metadata=self.metadata)

            tiller_result = TillerResult(
                install_msg.release.name,
                install_msg.release.namespace,
                install_msg.release.info.status.Code.Name(
                    install_msg.release.info.status.code),
                install_msg.release.info.Description,
                install_msg.release.version)

            return tiller_result
        except Exception:
            LOG.exception('Error while installing release %s', release)
            status = self.get_release_status(release)
            raise ex.ReleaseException(release, status, 'Install')

    def testing_release(self, release, timeout=300, cleanup=True):
        '''
        :param release - name of release to test
        :param timeout - runtime before exiting
        :param cleanup - removes testing pod created

        :returns - results of test pod
        '''

        LOG.debug("Helm test release %s, timeout=%s", release, timeout)

        try:

            stub = ReleaseServiceStub(self.channel)

            release_request = TestReleaseRequest(
                name=release, timeout=timeout, cleanup=cleanup)

            content = self.get_release_content(release)

            if not len(content.release.hooks):
                LOG.info('No test found')
                return False

            if content.release.hooks[0].events[0] == RUNTEST_SUCCESS:
                test = stub.RunReleaseTest(
                    release_request, self.timeout, metadata=self.metadata)

                if test.running():
                    self.k8s.wait_get_completed_podphase(release)

                test.cancel()

                return self.get_release_status(release)

        except Exception:
            LOG.exception('Error while testing release %s', release)
            status = self.get_release_status(release)
            raise ex.ReleaseException(release, status, 'Test')

    def get_release_status(self, release, version=0):
        '''
        :param release - name of release to test
        :param version - version of release status
        '''

        LOG.debug('Helm getting release status for release=%s, version=%s',
                  release, version)
        try:
            stub = ReleaseServiceStub(self.channel)
            status_request = GetReleaseStatusRequest(
                name=release, version=version)

            release_status = stub.GetReleaseStatus(
                status_request, self.timeout, metadata=self.metadata)
            LOG.debug('GetReleaseStatus= %s', release_status)
            return release_status

        except Exception:
            raise ex.GetReleaseStatusException(release, version)

    def get_release_content(self, release, version=0):
        '''
        :param release - name of release to test
        :param version - version of release status
        '''

        LOG.debug('Helm getting release content for release=%s, version=%s',
                  release, version)
        try:
            stub = ReleaseServiceStub(self.channel)
            status_request = GetReleaseContentRequest(
                name=release, version=version)

            release_content = stub.GetReleaseContent(
                status_request, self.timeout, metadata=self.metadata)
            LOG.debug('GetReleaseContent= %s', release_content)
            return release_content

        except Exception:
            raise ex.GetReleaseContentException(release, version)

    def tiller_version(self):
        '''
        :returns - Tiller version
        '''
        try:
            stub = ReleaseServiceStub(self.channel)
            release_request = GetVersionRequest()

            LOG.debug('Getting Tiller version, with timeout=%s', self.timeout)
            tiller_version = stub.GetVersion(
                release_request, self.timeout, metadata=self.metadata)

            tiller_version = getattr(tiller_version.Version, 'sem_ver', None)
            LOG.debug('Got Tiller version %s', tiller_version)
            return tiller_version

        except Exception:
            LOG.debug('Failed to get Tiller version')
            raise ex.TillerVersionException()

    def uninstall_release(self, release, disable_hooks=False, purge=True):
        '''
        :params - release - Helm chart release name
        :params - purge - deep delete of chart

        deletes a Helm chart from Tiller
        '''

        # build release install request
        try:
            stub = ReleaseServiceStub(self.channel)
            LOG.info("Uninstall %s release with disable_hooks=%s, "
                     "purge=%s flags", release, disable_hooks, purge)
            release_request = UninstallReleaseRequest(
                name=release, disable_hooks=disable_hooks, purge=purge)

            return stub.UninstallRelease(
                release_request, self.timeout, metadata=self.metadata)

        except Exception:
            LOG.exception('Error while uninstalling release %s', release)
            status = self.get_release_status(release)
            raise ex.ReleaseException(release, status, 'Delete')

    def chart_cleanup(self, prefix, charts):
        '''
        :params charts - list of yaml charts
        :params known_release - list of releases in tiller

        :result - will remove any chart that is not present in yaml
        '''

        valid_charts = []
        for gchart in charts:
            for chart in gchart.get('chart_group'):
                valid_charts.append(release_prefix(
                    prefix, chart.get('chart').get('name')))

        actual_charts = [x.name for x in self.list_releases()]
        chart_diff = list(set(actual_charts) - set(valid_charts))

        for chart in chart_diff:
            if chart.startswith(prefix):
                LOG.debug("Release: %s will be removed", chart)
                self.uninstall_release(chart)

    def delete_resources(self, release_name, resource_name, resource_type,
                         resource_labels, namespace, wait=False,
                         timeout=TILLER_TIMEOUT):
        '''
        :params release_name - release name the specified resource is under
        :params resource_name - name of specific resource
        :params resource_type - type of resource e.g. job, pod, etc.
        :params resource_labels - labels by which to identify the resource
        :params namespace - namespace of the resource

        Apply deletion logic based on type of resource
        '''

        label_selector = ''
        if resource_labels is not None:
            label_selector = label_selectors(resource_labels)
        LOG.debug("Deleting resources in namespace %s matching "
                  "selectors %s.", namespace, label_selector)

        handled = False
        if resource_type == 'job':
            get_jobs = self.k8s.get_namespace_job(namespace, label_selector)
            for jb in get_jobs.items:
                jb_name = jb.metadata.name
                LOG.info("Deleting job %s in namespace: %s",
                         jb_name, namespace)
                self.k8s.delete_job_action(jb_name, namespace, timeout=timeout)
            handled = True

        if resource_type == 'cronjob' or resource_type == 'job':
            get_jobs = self.k8s.get_namespace_cron_job(
                namespace, label_selector)
            for jb in get_jobs.items:
                jb_name = jb.metadata.name
                LOG.info("Deleting cron job %s in namespace: %s",
                         jb_name, namespace)
                if resource_type == 'job':
                    # TODO: Eventually disallow this, allowing initially since
                    #       some existing clients were expecting this behavior.
                    LOG.warning("Deleting cron jobs via `type: job` is "
                                "deprecated, use `type: cronjob` instead")
                self.k8s.delete_cron_job_action(jb_name, namespace)
            handled = True

        if resource_type == 'pod':
            release_pods = self.k8s.get_namespace_pod(
                namespace, label_selector)

            for pod in release_pods.items:
                pod_name = pod.metadata.name
                LOG.info("Deleting pod %s in namespace: %s",
                         pod_name, namespace)
                self.k8s.delete_namespace_pod(pod_name, namespace)
                if wait:
                    self.k8s.wait_for_pod_redeployment(pod_name, namespace)
            handled = True

        if not handled:
            LOG.error("Unable to execute name: %s type: %s ",
                      resource_name, resource_type)

    def rolling_upgrade_pod_deployment(self, name, release_name, namespace,
                                       resource_labels, action_type, chart,
                                       disable_hooks, values,
                                       timeout=TILLER_TIMEOUT):
        '''
        update statefullsets (daemon, stateful)
        '''

        if action_type == 'daemonset':

            LOG.info('Updating: %s', action_type)

            label_selector = ''

            if resource_labels is not None:
                label_selector = label_selectors(resource_labels)

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
                    self.delete_resources(
                        release_name, name, 'pod', resource_labels, namespace,
                        wait=True, timeout=timeout)

        else:
            LOG.error("Unable to exectue name: % type: %s", name, action_type)
