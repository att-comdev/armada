from armada.handlers.armada import Armada

import mock
import unittest
from threading import Thread
from time import sleep

POD_NAME_COUNTER = 1

class PodGenerator():

    def gen_pod(self, phase, message=None):
        global POD_NAME_COUNTER
        pod = mock.Mock()
        pod.status.phase = phase
        pod.metadata.name = 'pod_instance_{}'.format(POD_NAME_COUNTER)
        POD_NAME_COUNTER += 1
        if message:
            pod.status.message = message
        return pod


class WaitTestCase(unittest.TestCase):

    @mock.patch('armada.handlers.armada.lint')
    @mock.patch('armada.handlers.tiller.Tiller')
    def test_wait(self, mock_tiller, mock_lint):
        TIMEOUT = 5
        # instantiate Armada object
        armada = Armada("../../examples/openstack-helm.yaml",
                        wait=True,
                        timeout=TIMEOUT)
        armada.tiller = mock_tiller

        # TIMEOUT TEST
        timeout_pod = PodGenerator().gen_pod('Unknown')
        pods = mock.Mock()
        pods.items = [timeout_pod]
        mock_tiller.k8s.get_all_pods.return_value = pods

        with self.assertRaises(RuntimeError):
            armada.wait_for_deployment()
        mock_tiller.k8s.get_all_pods.assert_called_with()

        # FAILED_STATUS TEST
        failed_pod = PodGenerator().gen_pod('Failed')
        pods = mock.Mock()
        pods.items = [failed_pod]
        mock_tiller.k8s.get_all_pods.return_value = pods

        with self.assertRaises(RuntimeError):
            armada.wait_for_deployment()
        mock_tiller.k8s.get_all_pods.assert_called_with()

        # SUCCESS_STATUS TEST
        success_pod = PodGenerator().gen_pod('Succeeded')
        pods = mock.Mock()
        pods.items = [success_pod]
        mock_tiller.k8s.get_all_pods.return_value = pods

        try:
            armada.wait_for_deployment()
        except RuntimeError as e:
            self.fail('Expected success but got {}'.format(e))
        mock_tiller.k8s.get_all_pods.assert_called_with()

        # SIMULATE_DEPLOYMENT TEST
        simulation_pod = PodGenerator().gen_pod('Pending')
        pods = mock.Mock()
        pods.items = [simulation_pod]
        mock_tiller.k8s.get_all_pods.return_value = pods

        method_call = Thread(target=armada.wait_for_deployment)
        method_call.start()

        # let the method spin for a bit, then change pod status
        sleep(TIMEOUT / 4.0)
        simulation_pod.status.phase = 'Running'

        try:
            # ensure the method_call thread ends after status change
            method_call.join(5.0)
            self.assertFalse(method_call.is_alive())
        except RuntimeError as e:
            self.fail('Expected success but got {}'.format(e))
        mock_tiller.k8s.get_all_pods.assert_called_with()
