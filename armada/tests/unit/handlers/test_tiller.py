import mock
import unittest

# Required Oslo configuration setup
from armada.conf import default
default.register_opts()

from armada.handlers.tiller import Tiller

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
        timeout = None

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
                             tiller.timeout,
                             metadata=tiller.metadata))
