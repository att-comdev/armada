from armada.handlers.tiller import Tiller

import mock
import unittest

class TillerTestCase(unittest.TestCase):

    @mock.patch('armada.handlers.tiller.grpc')
    @mock.patch('armada.handlers.tiller.Config')
    @mock.patch('armada.handlers.tiller.InstallReleaseRequest')
    @mock.patch('armada.handlers.tiller.ReleaseServiceStub')
    def test_install_release(self, mock_stub, mock_install_request,
                             mock_config, mock_grpc):
        # instantiate Tiller object
        mock_grpc.insecure_channel.return_value = None
        tiller = Tiller()

        # set params
        chart = mock.Mock()
        dry_run = False
        name = None
        namespace = None
        prefix = None
        initial_values = None
        updated_values = mock_config(raw=initial_values)
        wait = False
        timeout = None

        tiller.install_release(chart, dry_run, name, namespace, prefix,
                               values=initial_values, wait=wait,
                               timeout=timeout)

        mock_stub.assert_called_with(tiller.channel)
        release_request = mock_install_request(
            chart=chart,
            dry_run=dry_run,
            values=updated_values,
            name="{}-{}".format(prefix, name),
            namespace=namespace,
            wait=wait,
            timeout=timeout
        )
        (mock_stub(tiller.channel).InstallRelease
         .assert_called_with(release_request,
                             tiller.timeout,
                             metadata=tiller.metadata))
