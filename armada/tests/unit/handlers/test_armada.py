import mock
import unittest
import yaml

# Required Oslo configuration setup
from armada.conf import default
default.register_opts()

from armada.handlers.armada import Armada

class ArmadaTestCase(unittest.TestCase):
    test_yaml = """
        endpoints: &endpoints
          hello-world:
            this: is an example

        armada:
          release_prefix: armada
          charts:
            - chart:
                name: test_chart_1
                release_name: test_chart_1
                namespace: test
                values: {}
                source:
                  type: null
                  location: null
                  subpath: null
                  reference: null
                dependencies: []
                timeout: 50

            - chart:
                name: test_chart_2
                release_name: test_chart_2
                namespace: test
                values: {}
                source:
                  type: null
                  location: null
                  subpath: null
                  reference: null
                dependencies: []
                timeout: 5
    """

    @mock.patch('armada.handlers.armada.ChartBuilder')
    @mock.patch('armada.handlers.armada.Tiller')
    def test_install(self, mock_tiller, mock_chartbuilder):
        '''Test install functionality from the sync() method'''

        # instantiate Armada and Tiller objects
        armada = Armada('',
                        skip_pre_flight=True,
                        wait=True,
                        timeout=None)
        armada.tiller = mock_tiller
        armada.config = yaml.load(self.test_yaml)

        chart_1 = armada.config['armada']['charts'][0]['chart']
        chart_2 = armada.config['armada']['charts'][1]['chart']

        # mock irrelevant methods called by armada.sync()
        mock_tiller.list_charts.return_value = []
        mock_chartbuilder.source_clone.return_value = None
        mock_chartbuilder.get_helm_chart.return_value = None
        mock_chartbuilder.source_cleanup.return_value = None

        armada.sync()

        # check params that should be passed to tiller.install_release()
        method_calls = [mock.call(mock_chartbuilder().get_helm_chart(),
                                  armada.dry_run, chart_1['release_name'],
                                  chart_1['namespace'],
                                  armada.config['armada']['release_prefix'],
                                  values=yaml.safe_dump(chart_1['values']),
                                  wait=armada.wait,
                                  timeout=chart_1['timeout']),
                        mock.call(mock_chartbuilder().get_helm_chart(),
                                  armada.dry_run, chart_2['release_name'],
                                  chart_2['namespace'],
                                  armada.config['armada']['release_prefix'],
                                  values=yaml.safe_dump(chart_2['values']),
                                  wait=armada.wait,
                                  timeout=chart_2['timeout'])]
        mock_tiller.install_release.assert_has_calls(method_calls)

    @unittest.skip('skipping update')
    def test_upgrade(self):
        '''Test upgrade functionality from the sync() method'''
        # TODO
