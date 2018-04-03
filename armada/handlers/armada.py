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

from armada.handlers.chartbuilder import ChartBuilder
from armada.handlers.manifest import Manifest
from armada.handlers.override import Override
from armada.handlers.tiller import Tiller
from armada.exceptions import armada_exceptions
from armada.exceptions import source_exceptions
from armada.exceptions import validate_exceptions
from armada.exceptions import tiller_exceptions
from armada.utils.release import release_prefix
from armada.utils import source
from armada.utils import validate
from armada import const

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
DEFAULT_TIMEOUT = 3600


class Armada(object):
    '''
    This is the main Armada class handling the Armada
    workflows
    '''

    def __init__(self,
                 documents,
                 disable_update_pre=False,
                 disable_update_post=False,
                 enable_chart_cleanup=False,
                 dry_run=False,
                 set_ovr=None,
                 tiller_should_wait=False,
                 tiller_timeout=DEFAULT_TIMEOUT,
                 tiller_host=None,
                 tiller_port=None,
                 tiller_namespace=None,
                 values=None,
                 target_manifest=None,
                 k8s_wait_attempts=1,
                 k8s_wait_attempt_sleep=1):
        '''
        Initialize the Armada engine and establish a connection to Tiller.

        :param List[dict] documents: Armada documents.
        :param bool disable_update_pre: Disable pre-update Tiller operations.
        :param bool disable_update_post: Disable post-update Tiller
            operations.
        :param bool enable_chart_cleanup: Clean up unmanaged charts.
        :param bool dry_run: Run charts without installing them.
        :param bool tiller_should_wait: Specifies whether Tiller should wait
            until all charts are deployed.
        :param int tiller_timeout: Specifies time Tiller should wait for charts
            to deploy until timing out.
        :param str tiller_host: Tiller host IP. Default is None.
        :param int tiller_port: Tiller host port. Default is
            ``CONF.tiller_port``.
        :param str tiller_namespace: Tiller host namespace. Default is
            ``CONF.tiller_namespace``.
        :param str target_manifest: The target manifest to run. Useful for
            specifying which manifest to run when multiple are available.
        :param int k8s_wait_attempts: The number of times to attempt waiting
            for pods to become ready.
        :param int k8s_wait_attempt_sleep: The time in seconds to sleep
            between attempts.
        '''
        tiller_port = tiller_port or CONF.tiller_port
        tiller_namespace = tiller_namespace or CONF.tiller_namespace

        self.disable_update_pre = disable_update_pre
        self.disable_update_post = disable_update_post
        self.enable_chart_cleanup = enable_chart_cleanup
        self.dry_run = dry_run
        self.tiller_should_wait = tiller_should_wait
        self.tiller_timeout = tiller_timeout
        self.tiller = Tiller(
            tiller_host=tiller_host, tiller_port=tiller_port,
            tiller_namespace=tiller_namespace, dry_run=dry_run)
        self.documents = Override(
            documents, overrides=set_ovr,
            values=values).update_manifests()
        self.k8s_wait_attempts = k8s_wait_attempts
        self.k8s_wait_attempt_sleep = k8s_wait_attempt_sleep
        self.manifest = Manifest(
            self.documents,
            target_manifest=target_manifest).get_manifest()

    def find_release_chart(self, known_releases, name):
        '''
        Find a release given a list of known_releases and a release name
        '''
        for chart_name, _, chart, values, _ in known_releases:
            if chart_name == name:
                return chart, values

    def pre_flight_ops(self):
        """Perform a series of checks and operations to ensure proper
        deployment.
        """
        # Ensure Tiller is available and manifest is valid
        if not self.tiller.tiller_status():
            raise tiller_exceptions.TillerServicesUnavailableException()

        valid, details = validate.validate_armada_documents(self.documents)

        if details:
            for msg in details:
                if msg.get('error', False):
                    LOG.error(msg.get('message', 'Unknown validation error.'))
                else:
                    LOG.debug(msg.get('message', 'Validation succeeded.'))
            if not valid:
                raise validate_exceptions.InvalidManifestException(
                    error_messages=details)

        result, msg_list = validate.validate_armada_manifests(self.documents)
        if not result:
            raise validate_exceptions.InvalidArmadaObjectException(
                details=','.join([m.get('message') for m in msg_list]))

        # Purge known releases that have failed and are in the current yaml
        prefix = self.manifest.get(const.KEYWORD_ARMADA).get(
            const.KEYWORD_PREFIX)
        failed_releases = self.get_releases_by_status(const.STATUS_FAILED)
        for release in failed_releases:
            for group in self.manifest.get(const.KEYWORD_ARMADA).get(
                    const.KEYWORD_GROUPS):
                for ch in group.get(const.KEYWORD_CHARTS):
                    ch_release_name = release_prefix(
                        prefix, ch.get('chart').get('chart_name'))
                    if release[0] == ch_release_name:
                        if self.dry_run:
                            LOG.info('Would purge failed release %s '
                                     'before deployment.', release[0])
                        else:
                            LOG.info('Purging failed release %s '
                                     'before deployment.', release[0])
                            self.tiller.uninstall_release(release[0])

        # Clone the chart sources
        #
        # We only support a git source type right now, which can also
        # handle git:// local paths as well
        repos = {}
        for group in self.manifest.get(const.KEYWORD_ARMADA).get(
                const.KEYWORD_GROUPS):
            for ch in group.get(const.KEYWORD_CHARTS):
                self.tag_cloned_repo(ch, repos)

                for dep in ch.get('chart').get('dependencies'):
                    self.tag_cloned_repo(dep, repos)

    def tag_cloned_repo(self, ch, repos):
        chart = ch.get('chart', {})
        chart_source = chart.get('source', {})
        location = chart_source.get('location')
        ct_type = chart_source.get('type')
        subpath = chart_source.get('subpath', '.')

        if ct_type == 'local':
            chart['source_dir'] = (location, subpath)
        elif ct_type == 'tar':
            LOG.info('Downloading tarball from: %s', location)

            if not CONF.certs:
                LOG.warn(
                    'Disabling server validation certs to extract charts')
                tarball_dir = source.get_tarball(location, verify=False)
            else:
                tarball_dir = source.get_tarball(location, verify=CONF.cert)

            chart['source_dir'] = (tarball_dir, subpath)
        elif ct_type == 'git':
            reference = chart_source.get('reference', 'master')
            repo_branch = (location, reference)

            if repo_branch not in repos:
                auth_method = chart_source.get('auth_method')
                proxy_server = chart_source.get('proxy_server')

                logstr = 'Cloning repo: {} from branch: {}'.format(
                    *repo_branch)
                if proxy_server:
                    logstr += ' proxy: {}'.format(proxy_server)
                if auth_method:
                    logstr += ' auth method: {}'.format(auth_method)
                LOG.info(logstr)

                repo_dir = source.git_clone(*repo_branch,
                                            proxy_server=proxy_server,
                                            auth_method=auth_method)
                repos[repo_branch] = repo_dir

                chart['source_dir'] = (repo_dir, subpath)
            else:
                chart['source_dir'] = (repos.get(repo_branch), subpath)
        else:
            chart_name = chart.get('chart_name')
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
        Synchronize Helm with the Armada Config(s)
        '''
        if self.dry_run:
            LOG.info('Armada is in DRY RUN mode, no changes being made.')

        msg = {'install': [], 'upgrade': [], 'diff': []}

        # TODO: (gardlt) we need to break up this func into a cleaner format
        LOG.info("Performing pre-flight operations.")
        self.pre_flight_ops()

        # extract known charts on tiller right now
        known_releases = self.tiller.list_charts()
        prefix = self.manifest.get(const.KEYWORD_ARMADA).get(
            const.KEYWORD_PREFIX)

        if known_releases is None:
            raise armada_exceptions.KnownReleasesException()

        for release in known_releases:
            LOG.debug("Release %s, Version %s found on Tiller", release[0],
                      release[1])

        for entry in self.manifest[const.KEYWORD_ARMADA][const.KEYWORD_GROUPS]:

            tiller_should_wait = self.tiller_should_wait
            tiller_timeout = self.tiller_timeout
            desc = entry.get('description', 'A Chart Group')
            chart_groups = entry.get(const.KEYWORD_CHARTS, [])
            test_chartgroup = entry.get('test_charts', False)

            if entry.get('sequenced', False) or test_chartgroup:
                tiller_should_wait = True

            LOG.info('Deploying: %s', desc)

            for chartgroup in chart_groups:
                chart = chartgroup.get('chart', {})
                values = chart.get('values', {})
                test_chart = chart.get('test', False)
                namespace = chart.get('namespace', None)
                release = chart.get('release', None)
                pre_actions = {}
                post_actions = {}

                if release is None:
                    continue

                if test_chart:
                    tiller_should_wait = True

                # retrieve appropriate timeout value
                # TODO(MarshM): chart's `data.timeout` should be deprecated
                #               to favor `data.wait.timeout`
                # TODO(MarshM) also: timeout logic seems to prefer chart values
                #                    over api/cli, probably should swap?
                #                    (caution: it always default to 3600,
                #                    take care to differentiate user input)
                if tiller_should_wait and tiller_timeout == DEFAULT_TIMEOUT:
                    tiller_timeout = chart.get('timeout', tiller_timeout)
                wait_values = chart.get('wait', {})
                wait_timeout = wait_values.get('timeout', tiller_timeout)
                wait_values_labels = wait_values.get('labels', {})

                chartbuilder = ChartBuilder(chart)
                protoc_chart = chartbuilder.get_helm_chart()

                # determine install or upgrade by examining known releases
                deployed_releases = [x[0] for x in known_releases]
                prefix_chart = release_prefix(prefix, release)

                if prefix_chart in deployed_releases:

                    # indicate to the end user what path we are taking
                    LOG.info("Attempting Upgrade release: %s", release)
                    # extract the installed chart and installed values from the
                    # latest release so we can compare to the intended state
                    apply_chart, apply_values = self.find_release_chart(
                        known_releases, prefix_chart)

                    upgrade = chart.get('upgrade', {})
                    disable_hooks = upgrade.get('no_hooks', False)

                    if upgrade:
                        upgrade_pre = upgrade.get('pre', {})
                        upgrade_post = upgrade.get('post', {})

                        if not self.disable_update_pre and upgrade_pre:
                            pre_actions = upgrade_pre

                        if not self.disable_update_post and upgrade_post:
                            post_actions = upgrade_post

                    # show delta for both the chart templates and the chart
                    # values
                    # TODO(alanmeadows) account for .files differences
                    # once we support those

                    upgrade_diff = self.show_diff(
                        chart, apply_chart, apply_values,
                        chartbuilder.dump(), values, msg)

                    if not upgrade_diff:
                        LOG.info("There are no updates found in this chart")
                        continue

                    # do actual update
                    LOG.info('Beginning Upgrade, wait: %s, %s',
                             tiller_should_wait, wait_timeout)
                    self.tiller.update_release(
                        protoc_chart,
                        prefix_chart,
                        namespace,
                        pre_actions=pre_actions,
                        post_actions=post_actions,
                        # dry_run=self.dry_run,
                        disable_hooks=disable_hooks,
                        values=yaml.safe_dump(values),
                        wait=tiller_should_wait,
                        timeout=wait_timeout)

                    if tiller_should_wait:
                        self.tiller.k8s.wait_until_ready(
                            release=prefix_chart,
                            labels=wait_values_labels,
                            namespace=namespace,
                            k8s_wait_attempts=self.k8s_wait_attempts,
                            k8s_wait_attempt_sleep=self.k8s_wait_attempt_sleep,
                            timeout=wait_timeout
                        )

                    msg['upgrade'].append(prefix_chart)

                # process install
                else:
                    LOG.info("Attempting Install release: %s", release)
                    LOG.info('Beginning Install, wait: %s, %s',
                             tiller_should_wait, wait_timeout)
                    self.tiller.install_release(
                        protoc_chart,
                        prefix_chart,
                        namespace,
                        # dry_run=self.dry_run,
                        values=yaml.safe_dump(values),
                        wait=tiller_should_wait,
                        timeout=wait_timeout)

                    if tiller_should_wait:
                        self.tiller.k8s.wait_until_ready(
                            release=prefix_chart,
                            labels=wait_values_labels,
                            namespace=namespace,
                            k8s_wait_attempts=self.k8s_wait_attempts,
                            k8s_wait_attempt_sleep=self.k8s_wait_attempt_sleep,
                            timeout=wait_timeout
                        )

                    msg['install'].append(prefix_chart)

                # LOG.debug("Cleaning up chart source in %s",
                #           chartbuilder.source_directory)

                # TODO(MarshM) this should handle chart vs chartgroup better
                if (test_chartgroup or test_chart):
                    if self.dry_run:
                        LOG.info('Skipping test (dry run): %s', prefix_chart)
                    else:
                        LOG.info('Testing: %s', prefix_chart)
                        resp = self.tiller.testing_release(prefix_chart)
                        test_status = getattr(resp.info.status,
                                            'last_test_suite_run', 'FAILED')
                        LOG.info("Test INFO: %s", test_status)
                        if resp:
                            LOG.info("PASSED: %s", prefix_chart)
                        else:
                            LOG.info("FAILED: %s", prefix_chart)

                # ################
                # END CHART LOOP #
                # ################

            # TODO(MarshM) does this need release/labels/namespace?
            # TODO(MarshM) consider the tiller_timeout according to above logic
            #       because it currently waits on the timeout from the last
            #       chart processed, certainly not expected behavior
            LOG.info('Final k8s wait after chartgroup %s, %s seconds',
                     desc, tiller_timeout)
            tiller_timeout = 10
            self.tiller.k8s.wait_until_ready(
                k8s_wait_attempts=self.k8s_wait_attempts,
                k8s_wait_attempt_sleep=self.k8s_wait_attempt_sleep,
                timeout=tiller_timeout)

            # #####################
            # END CHARTGROUP LOOP #
            # #####################

        LOG.info("Performing Post-Flight Operations")
        self.post_flight_ops()

        if self.enable_chart_cleanup:
            self.tiller.chart_cleanup(
                prefix,
                self.manifest[const.KEYWORD_ARMADA][const.KEYWORD_GROUPS])

        return msg

    def post_flight_ops(self):
        '''
        Operations to run after deployment process has terminated
        '''
        # Delete temp dirs used for deployment
        for group in self.manifest.get(const.KEYWORD_ARMADA).get(
                const.KEYWORD_GROUPS):
            for ch in group.get(const.KEYWORD_CHARTS):
                if ch.get('chart').get('source').get('type') == 'git':
                    source.source_cleanup(ch.get('chart').get('source_dir')[0])

    def show_diff(self, chart, installed_chart, installed_values, target_chart,
                  target_values, msg):
        '''
        Produce a unified diff of the installed chart vs our intention

        TODO(alanmeadows): This needs to be rewritten to produce better
        unified diff output
        '''

        source = str(installed_chart.SerializeToString()).split('\n')
        chart_diff = list(
            difflib.unified_diff(source, str(target_chart).split('\n')))

        chart_release = chart.get('release', None)

        if len(chart_diff) > 0:
            LOG.info("Chart Unified Diff (%s)", chart_release)
            diff_msg = []
            for line in chart_diff:
                diff_msg.append(line)
                LOG.debug(line)

            msg['diff'].append({'chart': diff_msg})

        values_diff = list(
            difflib.unified_diff(
                installed_values.split('\n'),
                yaml.safe_dump(target_values).split('\n')))

        if len(values_diff) > 0:
            LOG.info("Values Unified Diff (%s)", chart_release)
            diff_msg = []
            for line in values_diff:
                diff_msg.append(line)
                LOG.debug(line)
                msg['diff'].append({'values': diff_msg})

        result = (len(chart_diff) > 0) or (len(values_diff) > 0)

        return result
