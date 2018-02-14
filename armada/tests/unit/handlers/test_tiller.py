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

import mock
import unittest

from armada.handlers.tiller import Tiller
from armada.exceptions import tiller_exceptions as ex


class TillerTestCase(unittest.TestCase):

    @mock.patch.object(Tiller, '_get_tiller_ip')
    @mock.patch('armada.handlers.tiller.K8s')
    @mock.patch('armada.handlers.tiller.grpc')
    @mock.patch('armada.handlers.tiller.Config')
    @mock.patch('armada.handlers.tiller.InstallReleaseRequest')
    @mock.patch('armada.handlers.tiller.ReleaseServiceStub')
    def test_install_release(self, mock_stub, mock_install_request,
                             mock_config, mock_grpc, mock_k8s, mock_ip):
        # instantiate Tiller object
        mock_grpc.insecure_channel.return_value = None
        mock_ip.return_value = '0.0.0.0'
        tiller = Tiller()
        assert tiller._get_tiller_ip() == '0.0.0.0'

        # set params
        chart = mock.Mock()
        dry_run = False
        name = None
        namespace = None
        initial_values = None
        updated_values = mock_config(raw=initial_values)
        wait = False
        timeout = 3600

        tiller.install_release(chart, name, namespace,
                               dry_run=dry_run, values=initial_values,
                               wait=wait, timeout=timeout)

        mock_stub.assert_called_with(tiller.channel)
        release_request = mock_install_request(
            chart=chart,
            dry_run=dry_run,
            values=updated_values,
            release=name,
            namespace=namespace,
            wait=wait,
            timeout=timeout
        )
        (mock_stub(tiller.channel).InstallRelease
         .assert_called_with(release_request,
                             timeout + 60,
                             metadata=tiller.metadata))

    @mock.patch.object(Tiller, '_get_tiller_ip')
    @mock.patch('armada.handlers.tiller.K8s')
    @mock.patch('armada.handlers.tiller.grpc')
    @mock.patch('armada.handlers.tiller.Config')
    @mock.patch('armada.handlers.tiller.InstallReleaseRequest')
    @mock.patch('armada.handlers.tiller.ReleaseServiceStub')
    def test_get_channel(self, mock_stub, mock_install_request,
                         mock_config, mock_grpc, mock_k8s, mock_ip):

        # instantiate Tiller object
        mock_grpc.insecure_channel.return_value = 'connected'
        mock_ip.return_value = '1.1.1.1'
        tiller = Tiller()
        self.assertNotEqual(tiller.get_channel(), None)
        self.assertEqual(tiller.get_channel(), 'connected')

    @mock.patch.object(Tiller, '_get_tiller_ip')
    @mock.patch('armada.handlers.tiller.K8s')
    @mock.patch('armada.handlers.tiller.grpc')
    @mock.patch('armada.handlers.tiller.Config')
    @mock.patch('armada.handlers.tiller.InstallReleaseRequest')
    @mock.patch('armada.handlers.tiller.ReleaseServiceStub')
    def test_get_tiller_ip(self, mock_stub, mock_install_request,
                           mock_config, mock_grpc, mock_k8s,
                           mock_ip):
        # instantiate Tiller object
        mock_ip.return_value = '1.1.1.1'
        tiller = Tiller()
        self.assertEqual(tiller._get_tiller_ip(), '1.1.1.1')

    @mock.patch.object(Tiller, '_get_tiller_ip')
    @mock.patch('armada.handlers.tiller.K8s')
    @mock.patch('armada.handlers.tiller.grpc')
    @mock.patch('armada.handlers.tiller.Config')
    @mock.patch('armada.handlers.tiller.InstallReleaseRequest')
    @mock.patch('armada.handlers.tiller.ReleaseServiceStub')
    def test_get_tiller_pod_throws_exception(self, mock_stub,
                                             mock_install_request,
                                             mock_config, mock_grpc, mock_k8s,
                                             mock_ip):
        # instantiate Tiller object
        status = mock.Mock(pod_ip='0.0.0.0')
        metadata = mock.Mock(name='tiller-deploy-1898392')
        item = mock.Mock(metadata=metadata, status=status)
        items = mock.Mock(items=[item])
        mock_k8s.get_namespace_pod.return_value = items

        tiller = Tiller()
        self.assertRaises(ex.TillerPodNotRunningException,
                          tiller._get_tiller_pod)
