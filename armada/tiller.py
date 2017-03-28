from hapi.services.tiller_pb2 import ReleaseServiceStub, ListReleasesRequest, \
    InstallReleaseRequest, UpdateReleaseRequest
from hapi.chart.config_pb2 import Config
from kubernetes import client
from kubernetes.client.rest import ApiException
import grpc

from k8s import K8s
from logutil import LOG

TILLER_PORT = 44134
TILLER_VERSION = b'2.1.3'
TILLER_TIMEOUT = 300
RELEASE_LIMIT = 64

class Tiller(object):
    '''
    The Tiller class supports communication and requests to the Tiller Helm
    service over gRPC
    '''

    def __init__(self):

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
        return grpc.insecure_channel('%s:%s' % (tiller_ip, tiller_port))

    def _get_tiller_pod(self):
        '''
        Search all namespaces for a pod beginning with tiller-deploy*
        '''
        ret = self.k8s.client.list_pod_for_all_namespaces()
        for i in ret.items:
            # TODO(alanmeadows): this is a bit loose
            if i.metadata.name.startswith('tiller-deploy'):
                return i

    def _get_tiller_ip(self):
        '''
        Returns the tiller pod's IP address by searching all namespaces
        '''
        pod = self._get_tiller_pod()
        return pod.status.pod_ip

    def _get_tiller_port(self):
        '''Stub method to support arbitrary ports in the future'''
        return TILLER_PORT

    def list_releases(self):
        '''
        List Helm Releases
        '''
        releases = []
        stub = ReleaseServiceStub(self.channel)
        req = ListReleasesRequest(limit=RELEASE_LIMIT)
        release_list = stub.ListReleases(req, self.timeout,
                                         metadata=self.metadata)
        for y in release_list:
            releases.extend(y.releases)
        return releases

    def list_charts(self):
        '''
        List Helm Charts from Latest Releases

        Returns list of (name, version, chart, values)
        '''
        charts = []
        for latest_release in self.list_releases():
            try:
                charts.append((latest_release.name, latest_release.version,
                               latest_release.chart,
                               latest_release.config.raw))
            except IndexError:
                continue
        return charts

    def _pre_update_actions(self, actions, namespace):
        '''
        :params actions - array of items actions
        :params namespace - name of pod for actions
        '''
        try:
            for action in actions.get('delete'):
                name = action.get("name")
                action_type = action.get("type")
                if "job" in action_type:
                    LOG.info("Deleting %s in namespace: %s", name, namespace)
                    self.delete_job_action(name, namespace)
                    continue
                LOG.error("Unable to execute name: %s type: %s ", name, type)
        except Exception:
            LOG.debug("Could not delete anything, please check yaml")

        try:
            for action in actions.get('create'):
                name = action.get("name")
                action_type = action.get("type")
                if "job" in action_type:
                    LOG.info("Creating %s in namespace: %s", name, namespace)
                    self.create_job_action(name, action_type)
                    continue
        except Exception:
            LOG.debug("Could not delete anything, please check yaml")

    def _post_update_actions(self, actions, namespace):
        pass

    def delete_job_action(self, name, namespace):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        '''
        try:
            body = client.V1DeleteOptions()
            self.k8s.api_client.delete_namespaced_job(name=name,
                                                      namespace=namespace,
                                                      body=body)
        except ApiException as e:
            LOG.error("Exception when deleting a job: %s", e)

    def create_job_action(self, name, namespace):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        '''
        LOG.info("Created %s in namespace: %s", name, namespace)

    def update_release(self, chart, dry_run, name, namespace,
                       pre_actions={}, post_actions={},
                       disable_hooks=False, values=None):
        '''
        Update a Helm Release
        '''

        if values is None:
            values = Config(raw='')
        else:
            values = Config(raw=values)

        self._pre_update_actions(pre_actions, namespace)

        # build release install request
        stub = ReleaseServiceStub(self.channel)
        release_request = UpdateReleaseRequest(
            chart=chart,
            dry_run=dry_run,
            disable_hooks=disable_hooks,
            values=values,
            name=name)

        stub.UpdateRelease(release_request, self.timeout,
                           metadata=self.metadata)

        self._post_update_actions(post_actions, namespace)

    def install_release(self, chart, dry_run, name, namespace, values=None):
        '''
        Create a Helm Release
        '''

        if values is None:
            values = Config(raw='')
        else:
            values = Config(raw=values)

        # build release install request
        stub = ReleaseServiceStub(self.channel)
        release_request = InstallReleaseRequest(
            chart=chart,
            dry_run=dry_run,
            values=values,
            name=name,
            namespace=namespace)
        return stub.InstallRelease(release_request,
                                   self.timeout,
                                   metadata=self.metadata)
