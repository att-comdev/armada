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

import yaml

from cliff import command as cmd
from oslo_config import cfg
from oslo_log import log as logging

from armada import const
from armada.handlers.manifest import Manifest
from armada.handlers.tiller import Tiller
from armada.utils.release import release_prefix

LOG = logging.getLogger(__name__)

CONF = cfg.CONF


def testService(args):

    tiller = Tiller(tiller_host=args.tiller_host, tiller_port=args.tiller_port)
    known_release_names = [release[0] for release in tiller.list_charts()]

    if args.release:
        LOG.info("RUNNING: %s tests", args.release)
        resp = tiller.testing_release(args.release)

        if not resp:
            LOG.info("FAILED: %s", args.release)
            return

        test_status = getattr(resp.info.status, 'last_test_suite_run',
                              'FAILED')
        if test_status.results[0].status:
            LOG.info("PASSED: %s", args.release)
        else:
            LOG.info("FAILED: %s", args.release)

    if args.file:
        with open(args.file) as f:
            documents = yaml.safe_load_all(f.read())
            armada_obj = Manifest(documents).get_manifest()
            prefix = armada_obj.get(const.KEYWORD_ARMADA).get(
                const.KEYWORD_PREFIX)

            for group in armada_obj.get(const.KEYWORD_ARMADA).get(
                    const.KEYWORD_GROUPS):
                for ch in group.get(const.KEYWORD_CHARTS):
                    release_name = release_prefix(
                        prefix, ch.get('chart').get('chart_name'))

                    if release_name in known_release_names:
                        LOG.info('RUNNING: %s tests', release_name)
                        resp = tiller.testing_release(release_name)

                        if not resp:
                            continue

                        test_status = getattr(resp.info.status,
                                              'last_test_suite_run', 'FAILED')
                        if test_status.results[0].status:
                            LOG.info("PASSED: %s", release_name)
                        else:
                            LOG.info("FAILED: %s", release_name)

                    else:
                        LOG.info('Release %s not found - SKIPPING',
                                 release_name)


class TestServerCommand(cmd.Command):
    def get_parser(self, prog_name):
        parser = super(TestServerCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--release', action='store', help='testing Helm in Release')
        parser.add_argument(
            '-f',
            '--file',
            type=str,
            metavar='FILE',
            help='testing Helm releases in Manifest')
        parser.add_argument(
            '--tiller-host',
            action='store',
            type=str,
            default=None,
            help='Specify the tiller host')
        parser.add_argument(
            '--tiller-port',
            action='store',
            type=int,
            default=44134,
            help='Specify the tiller port')

        return parser

    def take_action(self, parsed_args):
        testService(parsed_args)
