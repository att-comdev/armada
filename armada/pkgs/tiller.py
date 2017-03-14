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

from hapi.services.tiller_pb2 import ReleaseServiceStub, ListReleasesRequest, \
    InstallReleaseRequest, UpdateReleaseRequest
from hapi.chart.config_pb2 import Config
from k8s import K8s
import grpc
import logging

LOG = logging.getLogger(__name__)

TILLER_PORT = 44134
TILLER_VERSION = b'2.1.3'
TILLER_TIMEOUT = 300

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
        try:
            ret = self.k8s.client.list_pod_for_all_namespaces()
            for i in ret.items:
                # TODO(alanmeadows): this is a bit loose
                if i.metadata.name.startswith('tiller-deploy'):
                    return i
        except Exception:
            LOG.error("Could not find the tiller service")

    def _get_tiller_ip(self):
        '''
        Returns the tiller pod's IP address by searching all namespaces
        '''
        LOG.info("Getting tiller IP")
        pod = self._get_tiller_pod()
        return pod.status.pod_ip

    def _get_tiller_port(self):
        '''Stub method to support arbitrary ports in the future'''
        return TILLER_PORT

    def list_releases(self):
        '''
        List Helm Releases
        '''
        try:
            stub = ReleaseServiceStub(self.channel)
            req = ListReleasesRequest()
            return stub.ListReleases(req, self.timeout, metadata=self.metadata)
        except Exception:
            LOG.error("Could not get List of Helm Releases")

    def list_charts(self):
        '''
        List Helm Charts from Latest Releases

        Returns list of (name, version, chart, values)
        '''
        charts = []
        for x in self.list_releases():
            try:
                latest_release = x.releases[-1]
                charts.append((latest_release.name, latest_release.version,
                               latest_release.chart,
                               latest_release.config.raw))
            except IndexError:
                continue
        return charts

    def update_release(self, chart, dry_run, name, disable_hooks=False,
                       values=None):
        '''
        Update a Helm Release
        '''

        if values is None:
            values = Config(raw='')
        else:
            values = Config(raw=values)

        # build release install request
        try:
            LOG.info("Updating the %s chart", chart)
            stub = ReleaseServiceStub(self.channel)
            release_request = UpdateReleaseRequest(
                chart=chart,
                dry_run=dry_run,
                disable_hooks=disable_hooks,
                values=values,
                name=name)
            return stub.UpdateRelease(release_request, self.timeout,
                                      metadata=self.metadata)
        except Exception:
            LOG.error("Could not update the helm release")

    def install_release(self, chart, dry_run, name, namespace, values=None):
        '''
        Create a Helm Release
        '''

        if values is None:
            values = Config(raw='')
        else:
            values = Config(raw=values)

        # build release install request
        try:
            LOG.debug("Installing the %s chart", chart)
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
        except Exception:
            LOG.error("Could not install realease")
            raise
