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

from armada.exceptions import tiller_exceptions as ex
from armada.handlers import tiller
from armada.tests.unit import base


class TillerTestCase(base.ArmadaTestCase):

    @mock.patch.object(tiller.Tiller, '_get_tiller_ip')
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
        tiller_obj = tiller.Tiller()
        assert tiller_obj._get_tiller_ip() == '0.0.0.0'

        # set params
        chart = mock.Mock()
        dry_run = False
        name = None
        namespace = None
        initial_values = None
        updated_values = mock_config(raw=initial_values)
        wait = False
        timeout = 3600

        tiller_obj.install_release(chart, name, namespace,
                                   dry_run=dry_run, values=initial_values,
                                   wait=wait, timeout=timeout)

        mock_stub.assert_called_with(tiller_obj.channel)
        release_request = mock_install_request(
            chart=chart,
            dry_run=dry_run,
            values=updated_values,
            release=name,
            namespace=namespace,
            wait=wait,
            timeout=timeout
        )
        (mock_stub(tiller_obj.channel).InstallRelease
         .assert_called_with(release_request,
                             timeout + 60,
                             metadata=tiller_obj.metadata))

    @mock.patch('armada.handlers.tiller.K8s', autospec=True)
    @mock.patch.object(tiller.Tiller, '_get_tiller_ip', autospec=True)
    @mock.patch.object(tiller.Tiller, '_get_tiller_port', autospec=True)
    @mock.patch('armada.handlers.tiller.grpc', autospec=True)
    def test_get_channel(self, mock_grpc, mock_port, mock_ip, _):
        mock_port.return_value = mock.sentinel.port
        mock_ip.return_value = mock.sentinel.ip

        # instantiate Tiller object
        mock_grpc.insecure_channel.return_value = 'connected'
        tiller_obj = tiller.Tiller()

        self.assertIsNotNone(tiller_obj.channel)
        self.assertEqual('connected', tiller_obj.channel)

        mock_grpc.insecure_channel.assert_called_once_with(
            '%s:%s' % (str(mock.sentinel.ip), str(mock.sentinel.port)),
            options=[('grpc.max_send_message_length',
                     tiller.MAX_MESSAGE_LENGTH),
                     ('grpc.max_receive_message_length',
                     tiller.MAX_MESSAGE_LENGTH)]
        )

    @mock.patch.object(tiller.Tiller, '_get_tiller_ip', autospec=True)
    @mock.patch('armada.handlers.tiller.K8s', autospec=True)
    @mock.patch('armada.handlers.tiller.grpc', autospec=True)
    def test_get_tiller_ip2(self, mock_grpc, _, mock_ip):
        # instantiate Tiller object
        mock_ip.return_value = '1.1.1.1'
        tiller_obj = tiller.Tiller()
        self.assertIsNotNone(tiller_obj._get_tiller_ip())
        self.assertEqual(tiller_obj._get_tiller_ip(), '1.1.1.1')

        mock_ip.return_value = mock.sentinel.ip
        self.assertEqual(tiller_obj._get_tiller_ip(), mock.sentinel.ip)

    @mock.patch.object(tiller.Tiller, '_get_tiller_ip', autospec=True)
    @mock.patch('armada.handlers.tiller.K8s', autospec=True)
    @mock.patch('armada.handlers.tiller.grpc', autospec=True)
    def test_get_tiller_pod_throws_exception(self, mock_grpc, mock_k8s,
                                             mock_ip):
        # instantiate Tiller object
        status = mock.Mock(pod_ip=mock.sentinel.ip)
        metadata = mock.Mock(name='tiller-deploy-1898392')
        item = mock.Mock(metadata=metadata, status=status)
        items = mock.Mock(items=[item])
        mock_k8s.get_namespace_pod.return_value = items

        tiller_obj = tiller.Tiller()
        mock_grpc.insecure_channel.side_effect = ex.ChannelException()

        self.assertRaises(ex.TillerPodNotRunningException,
                          tiller_obj._get_tiller_pod)

    @mock.patch.object(tiller.Tiller, '_get_tiller_ip', autospec=True)
    @mock.patch('armada.handlers.tiller.K8s', autospec=True)
    @mock.patch('armada.handlers.tiller.grpc', autospec=True)
    def test_get_tiller_port(self, mock_grpc, _, mock_ip):
        # instantiate Tiller object
        tiller_obj = tiller.Tiller(None, '8080', None)
        self.assertEqual(tiller_obj._get_tiller_port(), '8080')

    @mock.patch.object(tiller.Tiller, '_get_tiller_namespace', autospec=True)
    @mock.patch.object(tiller.Tiller, '_get_tiller_ip', autospec=True)
    @mock.patch('armada.handlers.tiller.K8s', autospec=True)
    @mock.patch('armada.handlers.tiller.grpc', autospec=True)
    def test_get_tiller_namespace(self, mock_grpc, _, mock_ip, mock_ns):
        # instantiate Tiller object
        tiller_obj = tiller.Tiller()
        mock_ns.return_value = mock.sentinel.namespace
        self.assertEqual(tiller_obj._get_tiller_namespace(),
                         mock.sentinel.namespace)

        # verifies namespace set by the mock_ns, not via instantiation
        tiller_obj2 = tiller.Tiller(None, None, 'test_namespace2')
        self.assertNotEqual(tiller_obj2._get_tiller_namespace(),
                            'test_namespace2')

    @mock.patch.object(tiller.Tiller, '_get_tiller_ip', autospec=True)
    @mock.patch('armada.handlers.tiller.K8s', autospec=True)
    @mock.patch('armada.handlers.tiller.grpc', autospec=True)
    def test_get_tiller_status(self, mock_grpc, _, mock_ip):
        # instantiate Tiller object
        tiller_obj = tiller.Tiller(None, '8080', None)
        self.assertEqual(tiller_obj.tiller_status(), True)
