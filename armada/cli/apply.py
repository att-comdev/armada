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

from armada.handlers.armada import Armada

def applyCharts(args):

    armada = Armada(open(args.file).read(),
                    args.disable_update_pre,
                    args.disable_update_post,
                    args.enable_chart_cleanup,
                    args.dry_run,
                    args.set,
                    args.wait,
                    args.timeout,
                    args.tiller_host,
                    args.tiller_port,
                    args.values,
                    args.debug_logging)
    armada.sync()

class ApplyChartsCommand(cmd.Command):
    def get_parser(self, prog_name):
        parser = super(ApplyChartsCommand, self).get_parser(prog_name)
        parser.add_argument('file', type=str, metavar='FILE',
                            help='Armada yaml file')
        parser.add_argument('--dry-run', action='store_true',
                            default=False, help='Run charts with dry run')
        parser.add_argument('--debug-logging', action='store_true',
                            default=False, help='Show debug logs')
        parser.add_argument('--disable-update-pre', action='store_true',
                            default=False, help='Disable pre upgrade actions')
        parser.add_argument('--disable-update-post', action='store_true',
                            default=False, help='Disable post upgrade actions')
        parser.add_argument('--enable-chart-cleanup', action='store_true',
                            default=False, help='Enable Chart Clean Up')
        parser.add_argument('--set', action='append', help='Override Armada'
                                                           'manifest values.')
        parser.add_argument('--wait', action='store_true',
                            default=False, help='Wait until all charts'
                                                'have been deployed')
        parser.add_argument('--timeout', action='store', type=int,
                            default=3600, help='Specifies time to wait'
                                                ' for charts to deploy')
        parser.add_argument('--tiller-host', action='store', type=str,
                            help='Specify the tiller host')

        parser.add_argument('--tiller-port', action='store', type=int,
                            default=44134, help='Specify the tiller port')

        parser.add_argument('--values', action='append',
                            help='Override manifest values with a yaml file')

        return parser

    def take_action(self, parsed_args):
        applyCharts(parsed_args)
