from supermutes.dot import dotify
from chartbuilder import ChartBuilder
from tiller import Tiller
from logutil import LOG
import yaml
import difflib

class Armada(object):
    '''
    This is the main Armada class handling the Armada
    workflows
    '''

    def __init__(self, args):
        '''
        Initialize the Armada Engine and establish
        a connection to Tiller
        '''

        self.args = args

        # internalize config
        self.config = yaml.load(open(args.config).read())

        self.tiller = Tiller()

    def find_release_chart(self, known_releases, name):
        '''
        Find a release given a list of known_releases and a release name
        '''
        for chart_name, version, chart, values in known_releases:
            if chart_name == name:
                return chart, values

    def sync(self):
        '''
        Syncronize Helm with the Armada Config(s)
        '''

        # extract known charts on tiller right now
        known_releases = self.tiller.list_charts()
        for release in known_releases:
            LOG.debug("Release %s, Version %s found on tiller", release[0],
                      release[1])

        for entry in self.config['armada']['charts']:

            chart = dotify(entry['chart'])
            values = entry['chart']['values']

            if chart.release_name is None:
                continue

            # initialize helm chart and request a
            # protoc helm chart object which will
            # pull the sources down and walk the
            # dependencies
            chartbuilder = ChartBuilder(chart)
            protoc_chart = chartbuilder.get_helm_chart()

            # determine install or upgrade by examining known releases
            if chart.release_name in [x[0] for x in known_releases]:

                # indicate to the end user what path we are taking
                LOG.info("Upgrading release %s", chart.release_name)

                # extract the installed chart and installed values from the
                # latest release so we can compare to the intended state
                installed_chart, installed_values = self.find_release_chart(
                    known_releases, chart.release_name)

                # show delta for both the chart templates and the chart values
                # TODO(alanmeadows) account for .files differences
                # once we support those

                upgrade_diff = self.show_diff(chart, installed_chart,
                                              installed_values,
                                              chartbuilder.dump(), values)

                if not upgrade_diff:
                    LOG.info("There are no updates found in this chart")
                    continue

                # do actual update
                self.tiller.update_release(protoc_chart, self.args.dry_run,
                                           chart.release_name,
                                           disable_hooks=chart.
                                           upgrade.no_hooks,
                                           values=yaml.safe_dump(values))

            # process install
            else:
                LOG.info("Installing release %s", chart.release_name)
                self.tiller.install_release(protoc_chart,
                                            self.args.dry_run,
                                            chart.release_name,
                                            chart.namespace,
                                            values=yaml.safe_dump(values))

            LOG.debug("Cleaning up chart source in %s",
                      chartbuilder.source_directory)
            chartbuilder.source_cleanup()

    def show_diff(self, chart, installed_chart,
                  installed_values, target_chart, target_values):
        '''
        Produce a unified diff of the installed chart vs our intention

        TODO(alanmeadows): This needs to be rewritten to produce better
        unified diff output and avoid the use of print
        '''

        chart_diff = list(difflib.unified_diff(installed_chart
                                               .SerializeToString()
                                               .split('\n'),
                                               target_chart.split('\n')))
        if len(chart_diff) > 0:
            LOG.info("Chart Unified Diff (%s)", chart.release_name)
            for line in chart_diff:
                LOG.debug(line)
        values_diff = list(difflib.unified_diff(installed_values.split('\n'),
                                                yaml
                                                .safe_dump(target_values)
                                                .split('\n')))
        if len(values_diff) > 0:
            LOG.info("Values Unified Diff (%s)", chart.release_name)
            for line in values_diff:
                LOG.debug(line)

        return (len(chart_diff) > 0) or (len(chart_diff) > 0)
