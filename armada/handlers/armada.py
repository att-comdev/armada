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

import difflib
import yaml

from oslo_config import cfg
from oslo_log import log as logging

from supermutes.dot import dotify

from chartbuilder import ChartBuilder
from tiller import Tiller
from ..utils.release import release_prefix
from ..utils import git
from ..utils import lint

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
DOMAIN = "armada"

logging.register_options(CONF)
logging.setup(CONF, DOMAIN)

LOG = logging.getLogger(__name__)

class Armada(object):
    '''
    This is the main Armada class handling the Armada
    workflows
    '''

    def __init__(self, config,
                 disable_update_pre=False,
                 disable_update_post=False,
                 enable_chart_cleanup=False,
                 skip_pre_flight=False,
                 dry_run=False):
        '''
        Initialize the Armada Engine and establish
        a connection to Tiller
        '''
        self.disable_update_pre = disable_update_pre
        self.disable_update_post = disable_update_post
        self.enable_chart_cleanup = enable_chart_cleanup
        self.skip_pre_flight = skip_pre_flight
        self.dry_run = dry_run
        self.config = yaml.load(config)
        self.tiller = Tiller()

    def find_release_chart(self, known_releases, name):
        '''
        Find a release given a list of known_releases and a release name
        '''
        for chart_name, _, chart, values in known_releases:
            if chart_name == name:
                return chart, values

    def pre_flight_checks(self):
        for ch in self.config['armada']['charts']:
            location = ch.get('chart').get('source').get('location')
            ct_type = ch.get('chart').get('source').get('type')

            if ct_type == 'git' and not git.check_available_repo(location):
                raise ValueError(str("Invalid Url Path: " + location))

            if not self.tiller.tiller_status():
                raise Exception("Tiller Services is not Available")

            if not lint.valid_manifest(self.config):
                raise Exception("Invalid Armada Manifest")

    def sync(self):
        '''
        Syncronize Helm with the Armada Config(s)
        '''

        # extract known charts on tiller right now
        if not self.skip_pre_flight:
            LOG.info("Performing Pre-Flight Checks")
            self.pre_flight_checks()
        else:
            LOG.info("Skipping Pre-Flight Checks")

        known_releases = self.tiller.list_charts()
        prefix = self.config.get('armada').get('release_prefix')

        for release in known_releases:
            LOG.debug("Release %s, Version %s found on tiller", release[0],
                      release[1])

        for entry in self.config['armada']['charts']:

            chart = dotify(entry['chart'])
            values = entry.get('chart').get('values', {})
            pre_actions = {}
            post_actions = {}

            if chart.release_name is None:
                continue

            # initialize helm chart and request a
            # protoc helm chart object which will
            # pull the sources down and walk the
            # dependencies
            chartbuilder = ChartBuilder(chart)
            protoc_chart = chartbuilder.get_helm_chart()

            # determine install or upgrade by examining known releases
            LOG.debug("RELEASE: %s", chart.release_name)

            if release_prefix(prefix, chart.release_name) in [x[0]
                                                              for x in
                                                              known_releases]:

                # indicate to the end user what path we are taking
                LOG.info("Upgrading release %s", chart.release_name)
                # extract the installed chart and installed values from the
                # latest release so we can compare to the intended state
                installed_chart, installed_values = self.find_release_chart(
                    known_releases, release_prefix(prefix, chart.release_name))

                LOG.info("Checking Pre/Post Actions")
                upgrade = entry.get('chart', {}).get('upgrade', False)
                if upgrade:
                    if not self.disable_update_pre and upgrade.get('pre',
                                                                   False):
                        pre_actions = getattr(chart.upgrade, 'pre', {})

                    if not self.disable_update_post and upgrade.get('post',
                                                                    False):
                        LOG.info("Checking Post Actions")
                        post_actions = getattr(chart.upgrade, 'post', {})

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
                self.tiller.update_release(protoc_chart,
                                           self.dry_run,
                                           chart.release_name,
                                           chart.namespace,
                                           prefix, pre_actions,
                                           post_actions,
                                           disable_hooks=chart.
                                           upgrade.no_hooks,
                                           values=yaml.safe_dump(values))

            # process install
            else:
                LOG.info("Installing release %s", chart.release_name)
                self.tiller.install_release(protoc_chart,
                                            self.dry_run,
                                            chart.release_name,
                                            chart.namespace,
                                            prefix,
                                            values=yaml.safe_dump(values))

            LOG.debug("Cleaning up chart source in %s",
                      chartbuilder.source_directory)

            chartbuilder.source_cleanup()

        if self.enable_chart_cleanup:
            self.tiller.chart_cleanup(prefix, self.config['armada']['charts'])

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

        return (len(chart_diff) > 0) or (len(values_diff) > 0)
