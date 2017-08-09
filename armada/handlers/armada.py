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
from manifest import Manifest
from override import Override

from ..exceptions import armada_exceptions
from ..exceptions import source_exceptions
from ..exceptions import lint_exceptions
from ..exceptions import tiller_exceptions

from ..utils.release import release_prefix
from ..utils import source
from ..utils import lint
from ..const import KEYWORD_ARMADA, KEYWORD_GROUPS, KEYWORD_CHARTS,\
    KEYWORD_PREFIX, STATUS_FAILED

LOG = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 3600
CONF = cfg.CONF


class Armada(object):
    '''
    This is the main Armada class handling the Armada
    workflows
    '''

    def __init__(self,
                 file,
                 disable_update_pre=False,
                 disable_update_post=False,
                 enable_chart_cleanup=False,
                 dry_run=False,
                 set_ovr=None,
                 wait=False,
                 timeout=DEFAULT_TIMEOUT,
                 tiller_host=None,
                 tiller_port=44134,
                 values=None,
                 debug=False):
        '''
        Initialize the Armada Engine and establish
        a connection to Tiller
        '''

        self.disable_update_pre = disable_update_pre
        self.disable_update_post = disable_update_post
        self.enable_chart_cleanup = enable_chart_cleanup
        self.dry_run = dry_run
        self.overrides = set_ovr
        self.wait = wait
        self.timeout = timeout
        self.tiller = Tiller(tiller_host=tiller_host, tiller_port=tiller_port)
        self.values = values
        self.documents = list(yaml.safe_load_all(file))
        self.config = None
        self.debug = debug

        # Set debug value
        # Define a default handler at INFO logging level
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)

    def get_armada_manifest(self):
        return Manifest(self.documents).get_manifest()

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

        # Ensure tiller is available and manifest is valid
        if not self.tiller.tiller_status():
            raise tiller_exceptions.TillerServicesUnavailableException()

        if not lint.validate_armada_documents(self.documents):
            raise lint_exceptions.InvalidManifestException()

        # Get config and validate
        self.config = self.get_armada_manifest()

        if not lint.validate_armada_object(self.config):
            raise lint_exceptions.InvalidArmadaObjectException()

        # Override manifest values if --set flag is used
        if self.overrides or self.values:
            self.config = Override(config=self.config,
                                   overrides=self.overrides,
                                   values=self.values).get_manifest()

        # Purge known releases that have failed and are in the current yaml
        prefix = self.config.get(KEYWORD_ARMADA).get(KEYWORD_PREFIX)
        failed_releases = self.get_releases_by_status(STATUS_FAILED)
        for release in failed_releases:
            for group in self.config.get(KEYWORD_ARMADA).get(KEYWORD_GROUPS):
                for ch in group.get(KEYWORD_CHARTS):
                    ch_release_name = release_prefix(prefix,
                                                     ch.get('chart')
                                                     .get('chart_name'))
                    if release[0] == ch_release_name:
                        LOG.info('Purging failed release %s '
                                 'before deployment', release[0])
                        self.tiller.uninstall_release(release[0])

        # Clone the chart sources
        #
        # We only support a git source type right now, which can also
        # handle git:// local paths as well
        repos = {}
        for group in self.config.get(KEYWORD_ARMADA).get(KEYWORD_GROUPS):
            for ch in group.get(KEYWORD_CHARTS):
                self.tag_cloned_repo(ch, repos)

                for dep in ch.get('chart').get('dependencies'):
                    self.tag_cloned_repo(dep, repos)

    def tag_cloned_repo(self, ch, repos):
        location = ch.get('chart').get('source').get('location')
        ct_type = ch.get('chart').get('source').get('type')
        reference = ch.get('chart').get('source').get('reference')
        subpath = ch.get('chart').get('source').get('subpath')

        if ct_type == 'local':
            ch.get('chart')['source_dir'] = (location, subpath)
        elif ct_type == 'tar':
            LOG.info('Downloading tarball from: %s', location)
            tarball_dir = source.get_tarball(location)
            ch.get('chart')['source_dir'] = (tarball_dir, subpath)
        elif ct_type == 'git':
            if location not in repos.keys():
                try:
                    LOG.info('Cloning repo: %s', location)
                    repo_dir = source.git_clone(location, reference)
                except Exception:
                    raise source_exceptions.GitLocationException(location)
                repos[location] = repo_dir
                ch.get('chart')['source_dir'] = (repo_dir, subpath)
            else:
                ch.get('chart')['source_dir'] = (repos.get(location), subpath)
        else:
            chart_name = ch.get('chart').get('chart_name')
            raise source_exceptions.ChartSourceException(ct_type, chart_name)

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
        prefix = self.config.get(KEYWORD_ARMADA).get(KEYWORD_PREFIX)

        if known_releases is None:
            raise armada_exceptions.KnownReleasesException()

        for release in known_releases:
            LOG.debug("Release %s, Version %s found on tiller", release[0],
                      release[1])

        for entry in self.config[KEYWORD_ARMADA][KEYWORD_GROUPS]:
            chart_wait = self.wait

            desc = entry.get('description', 'A Chart Group')
            chart_group = entry.get(KEYWORD_CHARTS, [])

            if entry.get('sequenced', False):
                chart_wait = True

            LOG.info('Deploying: %s', desc)

            for gchart in chart_group:
                chart = dotify(gchart['chart'])
                values = gchart.get('chart').get('values', {})
                pre_actions = {}
                post_actions = {}
                LOG.info('%s', chart.release)

                if chart.release is None:
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
                LOG.debug("RELEASE: %s", chart.release)
                deployed_releases = [x[0] for x in known_releases]
                prefix_chart = release_prefix(prefix, chart.release)

                if prefix_chart in deployed_releases:

                    # indicate to the end user what path we are taking
                    LOG.info("Upgrading release %s", chart.release)
                    # extract the installed chart and installed values from the
                    # latest release so we can compare to the intended state
                    LOG.info("Checking Pre/Post Actions")
                    apply_chart, apply_values = self.find_release_chart(
                        known_releases, prefix_chart)

                    LOG.info("Checking Pre/Post Actions")
                    upgrade = gchart.get('chart', {}).get('upgrade', False)

                    if upgrade:
                        if not self.disable_update_pre and upgrade.get(
                                'pre', False):
                            pre_actions = getattr(chart.upgrade, 'pre', {})

                        if not self.disable_update_post and upgrade.get(
                                'post', False):
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
                                               prefix_chart,
                                               chart.namespace,
                                               pre_actions=pre_actions,
                                               post_actions=post_actions,
                                               dry_run=self.dry_run,
                                               disable_hooks=chart.
                                               upgrade.no_hooks,
                                               values=yaml.safe_dump(values),
                                               wait=chart_wait,
                                               timeout=chart_timeout)

                # process install
                else:
                    LOG.info("Installing release %s", chart.release)
                    self.tiller.install_release(protoc_chart,
                                                prefix_chart,
                                                chart.namespace,
                                                dry_run=self.dry_run,
                                                values=yaml.safe_dump(values),
                                                wait=chart_wait,
                                                timeout=chart_timeout)

                LOG.debug("Cleaning up chart source in %s",
                          chartbuilder.source_directory)

        LOG.info("Performing Post-Flight Operations")
        self.post_flight_ops()

        if self.enable_chart_cleanup:
            self.tiller.chart_cleanup(
                prefix, self.config[KEYWORD_ARMADA][KEYWORD_GROUPS])

    def post_flight_ops(self):
        '''
        Operations to run after deployment process has terminated
        '''
        # Delete git repos cloned for deployment
        for group in self.config.get(KEYWORD_ARMADA).get(KEYWORD_GROUPS):
            for ch in group.get(KEYWORD_CHARTS):
                if ch.get('chart').get('source').get('type') == 'git':
                    source.source_cleanup(ch.get('chart').get('source_dir')[0])

    def show_diff(self, chart, installed_chart, installed_values, target_chart,
                  target_values):
        '''
        Produce a unified diff of the installed chart vs our intention

        TODO(alanmeadows): This needs to be rewritten to produce better
        unified diff output and avoid the use of print
        '''

        chart_diff = list(
            difflib.unified_diff(installed_chart.SerializeToString()
                                 .split('\n'), target_chart.split('\n')))
        if len(chart_diff) > 0:
            LOG.info("Chart Unified Diff (%s)", chart.release)
            for line in chart_diff:
                LOG.debug(line)
        values_diff = list(
            difflib.unified_diff(
                installed_values.split('\n'),
                yaml.safe_dump(target_values).split('\n')))
        if len(values_diff) > 0:
            LOG.info("Values Unified Diff (%s)", chart.release)
            for line in values_diff:
                LOG.debug(line)

        return (len(chart_diff) > 0) or (len(values_diff) > 0)
