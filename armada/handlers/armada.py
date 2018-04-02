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
            tiller_namespace=tiller_namespace)
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
        LOG.info("Performing pre-flight operations.")

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
        armada_data = self.manifest.get(const.KEYWORD_ARMADA, {})
        prefix = armada_data.get(const.KEYWORD_PREFIX, '')
        failed_releases = self.get_releases_by_status(const.STATUS_FAILED)

        for release in failed_releases:
            for group in armada_data.get(const.KEYWORD_GROUPS, []):
                for ch in group.get(const.KEYWORD_CHARTS, []):
                    ch_release_name = release_prefix(
                        prefix, ch.get('chart', {}).get('chart_name'))
                    if release[0] == ch_release_name:
                        LOG.info('Purging failed release %s '
                                 'before deployment', release[0])
                        self.tiller.uninstall_release(release[0])

        # Clone the chart sources
        #
        # We only support a git source type right now, which can also
        # handle git:// local paths as well
        repos = {}
        for group in armada_data.get(const.KEYWORD_GROUPS, []):
            for ch in group.get(const.KEYWORD_CHARTS, []):
                self.tag_cloned_repo(ch, repos)

                for dep in ch.get('chart', {}).get('dependencies', []):
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

    def get_releases_by_status(self, *statuses):
        '''
        Return the list of Tiller releases by the given ``statuses``.

        :param tuple statuses: Status strings to filter releases on.
        :returns: A list of current releases that match at least one of the
                  values in ``statuses``.
        :rtype: list
        '''
        filtered_releases = []
        known_releases = self.tiller.list_charts()

        for release in known_releases:
            if release[4] in statuses:
                filtered_releases.append(release)

        return filtered_releases

    def sync(self):
        '''
        Synchronize Helm with the Armada Config(s)
        '''

        msg = {'install': [], 'upgrade': [], 'diff': []}

        # TODO: (gardlt) we need to break up this func into a cleaner format.
        self.pre_flight_ops()

        # Retrieve currently deployed/failed charts from Tiller.
        known_releases = self.get_releases_by_status(const.STATUS_DEPLOYED,
                                                     const.STATUS_FAILED)
        armada_data = self.manifest.get(const.KEYWORD_ARMADA, {})
        prefix = armada_data.get(const.KEYWORD_PREFIX, '')

        for release in known_releases:
            LOG.debug("Release %s, Version %s found on Tiller", release[0],
                      release[1])

        for group in armada_data.get(const.KEYWORD_GROUPS, []):
            tiller_should_wait = self.tiller_should_wait
            tiller_timeout = self.tiller_timeout
            charts = group.get(const.KEYWORD_CHARTS, [])
            test_charts = group.get('test_charts', False)
            desc = group.get('description') or 'Chartgroup with name %s' % (
                group.get('name', 'Unspecified'))

            if group.get('sequenced', False) or test_charts:
                tiller_should_wait = True

            LOG.info('Deploying Chartgroup: %s', desc)

            for chart in charts:
                chart = chart.get('chart', {})
                values = chart.get('values', {})
                test_chart = chart.get('test', False)
                namespace = chart.get('namespace', None)
                release = chart.get('release', None)
                pre_actions = {}
                post_actions = {}

                if release is None:
                    continue

                if test_chart is True:
                    tiller_should_wait = True

                # Retrieve appropriate timeout value
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

                # Determine whether to install or upgrade the chart by
                # examining known, deployed releases.
                LOG.debug("Processing release=%s.", release)

                deployed_releases = [x[0] for x in known_releases]
                prefix_chart = release_prefix(prefix, release)

                # TODO(mark-burnett): It may be more robust to directly call
                # tiller status to decide whether to install/upgrade rather
                # than checking for list membership.
                if prefix_chart in deployed_releases:
                    # Indicate to the end user what path we are taking
                    LOG.info("Upgrading release %s", release)

                    # Extract the installed chart and installed values from the
                    # latest release so we can compare to the intended state
                    apply_chart, apply_values = self.find_release_chart(
                        known_releases, prefix_chart)

                    upgrade = chart.get('upgrade', {})
                    if upgrade:
                        LOG.info("Upgrading release=%s and processing "
                                 "pre/post actions for it.", release)
                        upgrade_pre = upgrade.get('pre', {})
                        upgrade_post = upgrade.get('post', {})

                        if not self.disable_update_pre and upgrade_pre:
                            pre_actions = upgrade_pre

                        if not self.disable_update_post and upgrade_post:
                            post_actions = upgrade_post
                    else:
                        pre_actions = post_actions = {}

                    # Show delta for both the chart templates and the chart
                    # values.
                    #
                    # TODO(alanmeadows): Account for .files differences
                    # once we support those.
                    LOG.info('Checking upgrade chart diffs.')
                    upgrade_diff = self.show_diff(
                        chart, apply_chart, apply_values,
                        chartbuilder.dump(), values, msg)

                    if not upgrade_diff:
                        LOG.info("There are no updates found in this chart")
                        continue

                    # Perform the actual update.
                    LOG.info('Beginning Upgrade, wait: %s, %s',
                             tiller_should_wait, wait_timeout)

                    disable_hooks = upgrade.get('no_hooks', False)
                    self.tiller.update_release(
                        protoc_chart,
                        prefix_chart,
                        namespace,
                        pre_actions=pre_actions,
                        post_actions=post_actions,
                        dry_run=self.dry_run,
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

                # Install the chart release instead as it currently hasn't
                # been deployed.
                else:
                    LOG.info("Installing release %s", release)
                    LOG.info('Beginning Install, wait: %s, %s',
                             tiller_should_wait, wait_timeout)
                    self.tiller.install_release(
                        protoc_chart,
                        prefix_chart,
                        namespace,
                        dry_run=self.dry_run,
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

                LOG.debug("Cleaning up chart source in %s",
                          chartbuilder.source_directory)

                if test_charts or (test_chart is True):
                    LOG.info('Testing: %s', prefix_chart)
                    resp = self.tiller.testing_release(prefix_chart)
                    test_status = getattr(resp.info.status,
                                          'last_test_suite_run', 'FAILED')
                    LOG.info("Test INFO: %s", test_status)
                    if resp:
                        LOG.info("PASSED: %s", prefix_chart)
                    else:
                        LOG.info("FAILED: %s", prefix_chart)

            # TODO(MarshM) does this need release/labels/namespace?
            # TODO(MarshM) consider the tiller_timeout according to above logic
            LOG.info('Wait after Chartgroup (%s) %ssec', desc, tiller_timeout)
            self.tiller.k8s.wait_until_ready(
                k8s_wait_attempts=self.k8s_wait_attempts,
                k8s_wait_attempt_sleep=self.k8s_wait_attempt_sleep,
                timeout=tiller_timeout)

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
        for group in self.manifest.get(const.KEYWORD_ARMADA, {}).get(
                const.KEYWORD_GROUPS, []):
            for ch in group.get(const.KEYWORD_CHARTS, []):
                chart = ch.get('chart', {})
                if chart.get('source', {}).get('type') == 'git':
                    source_dir = chart.get('source_dir')
                    if isinstance(source_dir, tuple) and source_dir:
                        source.source_cleanup(source_dir[0])

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
            diff_msg = []
            for line in chart_diff:
                diff_msg.append(line)
            msg['diff'].append({'chart': diff_msg})
            pretty_diff = '\n'.join(diff_msg).replace(
                '\\n', '\n').replace('\n\n', '\n')
            LOG.info("Found diff in chart (%s)", chart_release)
            LOG.debug(pretty_diff)

        values_diff = list(
            difflib.unified_diff(
                installed_values.split('\n'),
                yaml.safe_dump(target_values).split('\n')))

        if len(values_diff) > 0:
            diff_msg = []
            for line in values_diff:
                diff_msg.append(line)
            msg['diff'].append({'values': diff_msg})
            pretty_diff = '\n'.join(diff_msg).replace(
                '\\n', '\n').replace('\n\n', '\n')
            LOG.info("Found diff in chart values (%s)", chart_release)
            LOG.debug(pretty_diff)

        result = (len(chart_diff) > 0) or (len(values_diff) > 0)

        return result
