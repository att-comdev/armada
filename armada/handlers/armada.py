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

DEFAULT_TIMEOUT = 3600
CONF = cfg.CONF
DOMAIN = "armada"

logging.setup(CONF, DOMAIN)

class Armada(object):
    '''
    This is the main Armada class handling the Armada
    workflows
    '''

    def __init__(self, config,
                 disable_update_pre=False,
                 disable_update_post=False,
                 enable_chart_cleanup=False,
                 dry_run=False,
                 wait=False,
                 timeout=DEFAULT_TIMEOUT,
                 debug=False):
        '''
        Initialize the Armada Engine and establish
        a connection to Tiller
        '''
        self.disable_update_pre = disable_update_pre
        self.disable_update_post = disable_update_post
        self.enable_chart_cleanup = enable_chart_cleanup
        self.dry_run = dry_run
        self.wait = wait
        self.timeout = timeout
        self.config = yaml.load(config)
        self.tiller = Tiller()
        self.debug = debug

        # Set debug value
        CONF.set_default('debug', self.debug)
        logging.setup(CONF, DOMAIN)

    def find_release_chart(self, known_releases, name):
        '''
        Find a release given a list of known_releases and a release name
        '''
        for chart_name, _, chart, values, _ in known_releases:
            if chart_name == name:
                return chart, values

    def pre_flight_ops(self):
        '''
        Perform a series of checks and operations to ensure proper deployment
        '''
        # Ensure tiller is available and yaml is valid
        if not self.tiller.tiller_status():
            raise Exception("Tiller Services is not Available")
        if not lint.valid_manifest(self.config):
            raise Exception("Invalid Armada Manifest")

        # Purge known releases that have failed and are in the current yaml
        prefix = self.config.get('armada').get('release_prefix')
        failed_releases = self.get_releases_by_status('FAILED')
        for release in failed_releases:
            for group in self.config.get('armada').get('charts'):
                for ch in group.get('chart_group'):
                    ch_release_name = release_prefix(prefix, ch.get('chart')
                                                               .get('name'))
                    if release[0] == ch_release_name:
                        LOG.info('Purging failed release %s '
                                 'before deployment', release[0])
                        self.tiller.uninstall_release(release[0])

        # Clone the chart sources
        #
        # We only support a git source type right now, which can also
        # handle git:// local paths as well
        repos = {}
        for group in self.config.get('armada').get('charts'):
            for ch in group.get('chart_group'):
                location = ch.get('chart').get('source').get('location')
                ct_type = ch.get('chart').get('source').get('type')
                reference = ch.get('chart').get('source').get('reference')
                subpath = ch.get('chart').get('source').get('subpath')

                if ct_type == 'local':
                    ch.get('chart')['source_dir'] = (location, subpath)
                elif ct_type == 'git':
                    if location not in repos.keys():
                        try:
                            LOG.info('Cloning repo: %s', location)
                            repo_dir = git.git_clone(location, reference)
                        except Exception as e:
                            raise ValueError(e)
                        repos[location] = repo_dir
                        ch.get('chart')['source_dir'] = (repo_dir, subpath)
                    else:
                        ch.get('chart')['source_dir'] = (repos.get(location),
                                                         subpath)
                else:
                    raise Exception("Unknown source type %s for chart %s",
                                    ct_type, ch.get('chart').get('name'))

    def get_releases_by_status(self, status):
        '''
        :params status - status string to filter releases on

        Return a list of current releases with a specified status
        '''
        filtered_releases = []
        known_releases = self.tiller.list_charts()
        for release in known_releases:
            if release[4] == status:
                filtered_releases.append(release)

        return filtered_releases

    def sync(self):
        '''
        Syncronize Helm with the Armada Config(s)
        '''

        # TODO: (gardlt) we need to break up this func into
        # a more cleaner format
        LOG.info("Performing Pre-Flight Operations")
        self.pre_flight_ops()

        # extract known charts on tiller right now
        known_releases = self.tiller.list_charts()
        prefix = self.config.get('armada').get('release_prefix')

        for release in known_releases:
            LOG.debug("Release %s, Version %s found on tiller", release[0],
                      release[1])

        for entry in self.config['armada']['charts']:
            chart_wait = self.wait
            desc = entry.get('description', 'A Chart Group')
            chart_group = entry.get('chart_group', [])

            if entry.get('sequenced', False):
                chart_wait = True

            LOG.info('Deploying: %s', desc)

            for gchart in chart_group:
                chart = dotify(gchart['chart'])
                values = gchart.get('chart').get('values', {})
                pre_actions = {}
                post_actions = {}
                LOG.info('%s', chart.release_name)

                if chart.release_name is None:
                    continue

                # retrieve appropriate timeout value if 'wait' is specified
                chart_timeout = self.timeout
                if chart_wait:
                    if chart_timeout == DEFAULT_TIMEOUT:
                        chart_timeout = getattr(chart, 'timeout',
                                                chart_timeout)

                chartbuilder = ChartBuilder(chart)
                protoc_chart = chartbuilder.get_helm_chart()

                # determine install or upgrade by examining known releases
                LOG.debug("RELEASE: %s", chart.release_name)
                deployed_releases = [x[0] for x in known_releases]
                prefix_chart = release_prefix(prefix, chart.release_name)

                if prefix_chart in deployed_releases:

                    # indicate to the end user what path we are taking
                    LOG.info("Upgrading release %s", chart.release_name)
                    # extract the installed chart and installed values from the
                    # latest release so we can compare to the intended state
                    LOG.info("Checking Pre/Post Actions")
                    apply_chart, apply_values = self.find_release_chart(
                        known_releases, prefix_chart)

                    LOG.info("Checking Pre/Post Actions")
                    upgrade = gchart.get('chart', {}).get('upgrade', False)

                    if upgrade:
                        if not self.disable_update_pre and upgrade.get('pre',
                                                                       False):
                            pre_actions = getattr(chart.upgrade, 'pre', {})

                        if not self.disable_update_post and upgrade.get('post',
                                                                        False):
                            post_actions = getattr(chart.upgrade, 'post', {})

                    # show delta for both the chart templates and the chart
                    # values
                    # TODO(alanmeadows) account for .files differences
                    # once we support those

                    upgrade_diff = self.show_diff(chart, apply_chart,
                                                  apply_values,
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
                                               values=yaml.safe_dump(values),
                                               wait=chart_wait,
                                               timeout=chart_timeout)

                # process install
                else:
                    LOG.info("Installing release %s", chart.release_name)
                    self.tiller.install_release(protoc_chart,
                                                self.dry_run,
                                                chart.release_name,
                                                chart.namespace,
                                                prefix,
                                                values=yaml.safe_dump(values),
                                                wait=chart_wait,
                                                timeout=chart_timeout)

                LOG.debug("Cleaning up chart source in %s",
                          chartbuilder.source_directory)

        LOG.info("Performing Post-Flight Operations")
        self.post_flight_ops()

        if self.enable_chart_cleanup:
            self.tiller.chart_cleanup(prefix, self.config['armada']['charts'])

    def post_flight_ops(self):
        '''
        Operations to run after deployment process has terminated
        '''
        # Delete git repos cloned for deployment
        for group in self.config.get('armada').get('charts'):
            for ch in group.get('chart_group'):
                if ch.get('chart').get('source').get('type') == 'git':
                    git.source_cleanup(ch.get('chart').get('source_dir')[0])

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
