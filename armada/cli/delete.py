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

from cliff import command as cmd
import yaml

import armada.const as const
from armada.handlers.manifest import Manifest
from armada.utils.release import release_prefix
from armada.handlers.tiller import Tiller

from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

CONF = cfg.CONF

def deleteCharts(args):
    '''
    Delete currently deployed helm charts from a file or by release name
    '''
    tiller = Tiller(tiller_host=args.tiller_host, tiller_port=args.tiller_port)
    known_release_names = [release[0] for release in tiller.list_charts()]

    if args.file:
        documents = yaml.safe_load_all(open(args.file).read())
        manifest = Manifest(documents).get_manifest().get(const.KEYWORD_ARMADA)
        prefix = manifest.get(const.KEYWORD_PREFIX)

        for group in manifest.get(const.KEYWORD_GROUPS):
            for ch in group.get(const.KEYWORD_CHARTS):
                release_name = release_prefix(
                    prefix, ch.get('chart').get('chart_name'))
                if release_name in known_release_names:
                    LOG.info('Deleting release %s', release_name)
                    tiller.uninstall_release(release_name)
                else:
                    LOG.info('Release %s not found - SKIPPING', release_name)

    if args.release_name:
        release_name = args.release_name
        if release_name in known_release_names:
            LOG.info('Deleting release %s', release_name)
            tiller.uninstall_release(release_name)
        else:
            LOG.info('Release %s not found - SKIPPING', release_name)

class DeleteChartsCommand(cmd.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteChartsCommand, self).get_parser(prog_name)
        parser.add_argument('-f', '--file', type=str, metavar='FILE',
                            help='Armada manifest of charts to delete')
        parser.add_argument('--release_name', type=str,
                            help='Name of release to delete')
        parser.add_argument('--tiller-host', action='store', type=str,
                            default=None, help='Specify the tiller host')
        parser.add_argument('--tiller-port', action='store', type=int,
                            default=44134, help='Specify the tiller port')
        self.parser = parser
        return parser

    def take_action(self, parsed_args):
        if not (parsed_args.file or parsed_args.release_name):
            self.parser.error(
                'No action requested, add --file or --release_name')
        deleteCharts(parsed_args)
