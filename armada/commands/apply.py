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

import logging

from cliff import command as cmd

from armada.pkgs.armada import Armada

LOG = logging.getLogger(__name__)

def applyCharts(args):
    armada = Armada(args)
    armada.sync()

class ApplyChartsCommand(cmd.Command):
    def get_parser(self, prog_name):
        parser = super(ApplyChartsCommand, self).get_parser(prog_name)
        parser.add_argument('file', type=str, metavar='FILE',
                            help='Armada yaml file')
        parser.add_argument('--dry-run', action='store_true',
                            default=False, help='Run charts with dry run')
        parser.add_argument('--debug', action='store',
                            default=False, help='Run charts with dry run')
        return parser

    def take_action(self, parsed_args):
        applyCharts(parsed_args)
