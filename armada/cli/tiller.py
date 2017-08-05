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

from armada.handlers.tiller import Tiller

from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

CONF = cfg.CONF

def tillerServer(args):

    tiller = Tiller()

    if args.status:
        LOG.info('Tiller is Active: %s', tiller.tiller_status())

    if args.releases:
        for release in tiller.list_releases():
            LOG.info("Release: %s ( namespace= %s )", release.name,
                     release.namespace)

class TillerServerCommand(cmd.Command):
    def get_parser(self, prog_name):
        parser = super(TillerServerCommand, self).get_parser(prog_name)
        parser.add_argument('--status', action='store_true',
                            default=False, help='Check Tiller service')
        parser.add_argument('--releases', action='store_true',
                            default=False, help='List Tiller Releases')
        return parser

    def take_action(self, parsed_args):
        tillerServer(parsed_args)
