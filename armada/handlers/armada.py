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
import time
import yaml

from oslo_config import cfg
from oslo_log import log as logging

from armada.handlers.chartbuilder import ChartBuilder
from armada.handlers.manifest import Manifest
from armada.handlers.override import Override
from armada.handlers.tiller import Tiller
from armada.exceptions.armada_exceptions import ArmadaTimeoutException
from armada.exceptions import source_exceptions
from armada.exceptions import validate_exceptions
from armada.exceptions import tiller_exceptions
from armada.utils.release import release_prefix
from armada.utils import source
from armada.utils import validate

from armada.const import DEFAULT_CHART_TIMEOUT
from armada.const import KEYWORD_ARMADA
from armada.const import KEYWORD_CHARTS
from armada.const import KEYWORD_GROUPS
from armada.const import KEYWORD_PREFIX
from armada.const import STATUS_FAILED

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


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
                 force_wait=False,
                 timeout=0,
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
        :param bool force_wait: Force Tiller to wait until all charts are
            deployed, rather than using each chart's specified wait policy.
        :param int timeout: Specifies overall time in seconds that Tiller
            should wait for charts until timing out.
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
        self.force_wait = force_wait
        self.timeout = timeout
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
        manifest_data = self.manifest.get(KEYWORD_ARMADA, {})
        prefix = manifest_data.get(KEYWORD_PREFIX, '')
        failed_releases = self.get_releases_by_status(STATUS_FAILED)

        for release in failed_releases:
            for group in manifest_data.get(KEYWORD_GROUPS, []):
                for ch in group.get(KEYWORD_CHARTS, []):
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
        for group in manifest_data.get(KEYWORD_GROUPS, []):
            for ch in group.get(KEYWORD_CHARTS, []):
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

        msg = {'install': [], 'upgrade': [], 'diff': []}

        # TODO: (gardlt) we need to break up this func into
        # a more cleaner format
        self.pre_flight_ops()

        # extract known charts on tiller right now
        known_releases = self.tiller.list_charts()
        manifest_data = self.manifest.get(KEYWORD_ARMADA, {})
        prefix = manifest_data.get(KEYWORD_PREFIX, '')

        for chartgroup in manifest_data.get(KEYWORD_GROUPS, []):
            cg_name = chartgroup.get('name', '<missing name>')
            cg_desc = chartgroup.get('description', '<missing description>')
            LOG.info('Processing ChartGroup: %s (%s)', cg_name, cg_desc)

            cg_sequenced = chartgroup.get('sequenced', False)
            cg_test_all_charts = chartgroup.get('test_charts', False)

            ns_label_set = set()
            tests_to_run = []

            cg_charts = chartgroup.get(KEYWORD_CHARTS, [])

            # Track largest Chart timeout to stop the ChartGroup at the end
            cg_max_timeout = 0

            for chart_entry in cg_charts:
                chart = chart_entry.get('chart', {})
                namespace = chart.get('namespace')
                release = chart.get('release')
                values = chart.get('values', {})
                pre_actions = {}
                post_actions = {}

                wait_timeout = self.timeout
                wait_labels = {}

                release_name = release_prefix(prefix, release)

                # Retrieve appropriate timeout value
                if wait_timeout <= 0:
                    # TODO(MarshM): chart's `data.timeout` should be deprecated
                    chart_timeout = chart.get('timeout', 0)
                    # Favor data.wait.timeout over data.timeout, until removed
                    wait_values = chart.get('wait', {})
                    wait_timeout = wait_values.get('timeout', chart_timeout)
                    wait_labels = wait_values.get('labels', {})

                # Determine wait logic
                this_chart_should_wait = (
                    cg_sequenced or self.force_wait or
                    wait_timeout > 0 or len(wait_labels) > 0) and (
                        not self.dry_run)

                if this_chart_should_wait and wait_timeout <= 0:
                    LOG.warn('No Chart timeout specified, using default: %ss',
                             DEFAULT_CHART_TIMEOUT)
                    wait_timeout = DEFAULT_CHART_TIMEOUT

                # Naively take largest timeout to apply at end
                # TODO(MarshM) better handling of timeout/timer
                cg_max_timeout = max(wait_timeout, cg_max_timeout)

                # Chart test policy can override ChartGroup, if specified
                test_this_chart = chart.get('test', cg_test_all_charts) and (
                    not self.dry_run)

                chartbuilder = ChartBuilder(chart)
                protoc_chart = chartbuilder.get_helm_chart()

                deployed_releases = [x[0] for x in known_releases]

                # Begin Chart timeout deadline
                deadline = time.time() + wait_timeout

                # TODO(mark-burnett): It may be more robust to directly call
                # tiller status to decide whether to install/upgrade rather
                # than checking for list membership.
                if release_name in deployed_releases:

                    # indicate to the end user what path we are taking
                    LOG.info("Upgrading release %s in namespace %s",
                             release_name, namespace)
                    # extract the installed chart and installed values from the
                    # latest release so we can compare to the intended state
                    apply_chart, apply_values = self.find_release_chart(
                        known_releases, release_name)

                    upgrade = chart.get('upgrade', {})
                    disable_hooks = upgrade.get('no_hooks', False)

                    LOG.info("Checking Pre/Post Actions")
                    if upgrade:
                        upgrade_pre = upgrade.get('pre', {})
                        upgrade_post = upgrade.get('post', {})

                        if not self.disable_update_pre and upgrade_pre:
                            pre_actions = upgrade_pre

                        if not self.disable_update_post and upgrade_post:
                            post_actions = upgrade_post

                    # Show delta for both the chart templates and the chart
                    # values
                    # TODO(alanmeadows) account for .files differences
                    # once we support those
                    LOG.info('Checking upgrade chart diffs.')
                    upgrade_diff = self.show_diff(
                        chart, apply_chart, apply_values,
                        chartbuilder.dump(), values, msg)

                    if not upgrade_diff:
                        LOG.info("There are no updates found in this chart")
                        continue

                    # TODO(MarshM): Add tiller dry-run before upgrade and
                    # consider deadline impacts

                    # do actual update
                    timer = int(round(deadline - time.time()))
                    LOG.info('Beginning Upgrade, wait=%s, timeout=%ss',
                             this_chart_should_wait, timer)
                    tiller_result = self.tiller.update_release(
                        protoc_chart,
                        release_name,
                        namespace,
                        pre_actions=pre_actions,
                        post_actions=post_actions,
                        dry_run=self.dry_run,
                        disable_hooks=disable_hooks,
                        values=yaml.safe_dump(values),
                        wait=this_chart_should_wait,
                        timeout=timer)

                    if this_chart_should_wait:
                        self.tiller.k8s.wait_until_ready(
                            release=release_name,
                            labels=wait_labels,
                            namespace=namespace,
                            k8s_wait_attempts=self.k8s_wait_attempts,
                            k8s_wait_attempt_sleep=self.k8s_wait_attempt_sleep,
                            timeout=timer
                        )

                    # Track namespace+labels touched by update
                    ns_label_set.add((namespace, tuple(wait_labels.items())))

                    LOG.info('Upgrade completed with results from Tiller: %s',
                             tiller_result.__dict__)
                    msg['upgrade'].append(release_name)

                # process install
                else:
                    LOG.info("Installing release %s in namespace %s",
                             release_name, namespace)

                    timer = int(round(deadline - time.time()))
                    LOG.info('Beginning Install, wait=%s, timeout=%ss',
                             this_chart_should_wait, timer)
                    tiller_result = self.tiller.install_release(
                        protoc_chart,
                        release_name,
                        namespace,
                        dry_run=self.dry_run,
                        values=yaml.safe_dump(values),
                        wait=this_chart_should_wait,
                        timeout=timer)

                    if this_chart_should_wait:
                        self.tiller.k8s.wait_until_ready(
                            release=release_name,
                            labels=wait_labels,
                            namespace=namespace,
                            k8s_wait_attempts=self.k8s_wait_attempts,
                            k8s_wait_attempt_sleep=self.k8s_wait_attempt_sleep,
                            timeout=timer
                        )

                    # Track namespace+labels touched by install
                    ns_label_set.add((namespace, tuple(wait_labels.items())))

                    LOG.info('Install completed with results from Tiller: %s',
                             tiller_result.__dict__)
                    msg['install'].append(release_name)

                # Sequenced ChartGroup should run tests after each Chart
                timer = int(round(deadline - time.time()))
                if test_this_chart and cg_sequenced:
                    LOG.info('Running sequenced test, timeout remaining: %ss.',
                             timer)
                    if timer <= 0:
                        reason = ('Timeout expired before testing sequenced '
                                  'release %s' % release_name)
                        LOG.error(reason)
                        raise ArmadaTimeoutException(reason)
                    self._test_chart(release_name, timer)
                    # TODO(MarshM): handle test failure or timeout

                # Un-sequenced ChartGroup should run tests at the end
                elif test_this_chart:
                    # Keeping track of time remaining
                    tests_to_run.append((release_name, timer))

            # End of Charts in ChartGroup
            LOG.info('All Charts applied in ChartGroup %s.', cg_name)

            # After all Charts are applied, we should wait for the entire
            # ChartGroup to become healthy by looking at the namespaces seen
            # TODO(MarshM): Need to restrict to only releases we processed
            # TODO(MarshM): Need to determine a better timeout
            #               (not cg_max_timeout)
            if cg_max_timeout <= 0:
                cg_max_timeout = DEFAULT_CHART_TIMEOUT
            deadline = time.time() + cg_max_timeout
            for (ns, labels) in ns_label_set:
                labels_dict = dict(labels)
                timer = int(round(deadline - time.time()))
                LOG.info('Final wait for healthy namespace (%s), label=(%s), '
                         'timeout remaining: %ss.', ns, labels_dict, timer)
                if timer <= 0:
                    reason = ('Timeout expired waiting on namespace: %s, '
                              'label: %s' % (ns, labels_dict))
                    LOG.error(reason)
                    raise ArmadaTimeoutException(reason)

                self.tiller.k8s.wait_until_ready(
                    namespace=ns,
                    labels=labels_dict,
                    k8s_wait_attempts=self.k8s_wait_attempts,
                    k8s_wait_attempt_sleep=self.k8s_wait_attempt_sleep,
                    timeout=timer)

            # After entire ChartGroup is healthy, run any pending tests
            for (test, test_timer) in tests_to_run:
                self._test_chart(test, test_timer)
                # TODO(MarshM): handle test failure or timeout

        LOG.info('Performing Post-Flight Operations.')
        self.post_flight_ops()

        if self.enable_chart_cleanup:
            self.tiller.chart_cleanup(
                prefix,
                self.manifest[KEYWORD_ARMADA][KEYWORD_GROUPS])

        LOG.info('Done processing manifest.')
        return msg

    def post_flight_ops(self):
        '''
        Operations to run after deployment process has terminated
        '''
        # Delete temp dirs used for deployment
        for group in self.manifest.get(KEYWORD_ARMADA, {}).get(
                KEYWORD_GROUPS, []):
            for ch in group.get(KEYWORD_CHARTS, []):
                chart = ch.get('chart', {})
                if chart.get('source', {}).get('type') == 'git':
                    source_dir = chart.get('source_dir')
                    if isinstance(source_dir, tuple) and source_dir:
                        source.source_cleanup(source_dir[0])

    def _test_chart(self, release_name, timeout):
        # TODO(MarshM): Fix testing, it's broken, and track timeout
        resp = self.tiller.testing_release(release_name, timeout=timeout)
        status = getattr(resp.info.status, 'last_test_suite_run', 'FAILED')
        LOG.info("Test info.status: %s", status)
        if resp:
            LOG.info("Test passed for release: %s", release_name)
            return True
        else:
            LOG.info("Test failed for release: %s", release_name)
            return False

    def show_diff(self, chart, installed_chart, installed_values, target_chart,
                  target_values, msg):
        '''Produce a unified diff of the installed chart vs our intention'''

        # TODO(MarshM) This gives decent output comparing values. Would be
        # nice to clean it up further. Are \\n or \n\n ever valid diffs?
        # Can these be cleanly converted to dicts, for easier compare?
        def _sanitize_diff_str(str):
            return str.replace('\\n', '\n').replace('\n\n', '\n').split('\n')

        source = _sanitize_diff_str(str(installed_chart.SerializeToString()))
        target = _sanitize_diff_str(str(target_chart))
        chart_diff = list(difflib.unified_diff(source, target, n=0))

        chart_release = chart.get('release', None)

        if len(chart_diff) > 0:
            LOG.info("Found diff in Chart (%s)", chart_release)
            diff_msg = []
            for line in chart_diff:
                diff_msg.append(line)
            msg['diff'].append({'chart': diff_msg})

            pretty_diff = '\n'.join(diff_msg)
            LOG.debug(pretty_diff)

        source = _sanitize_diff_str(installed_values)
        target = _sanitize_diff_str(yaml.safe_dump(target_values))
        values_diff = list(difflib.unified_diff(source, target, n=0))

        if len(values_diff) > 0:
            LOG.info("Found diff in values (%s)", chart_release)
            diff_msg = []
            for line in values_diff:
                diff_msg.append(line)
            msg['diff'].append({'values': diff_msg})

            pretty_diff = '\n'.join(diff_msg)
            LOG.debug(pretty_diff)

        result = (len(chart_diff) > 0) or (len(values_diff) > 0)

        return result
