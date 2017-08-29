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

def testService(args):

    tiller = Tiller()

    LOG.info("RUNNING: %s tests", args.release)
    if tiller.testing_release(args.release) is None:
        LOG.info("PASSED: %s", args.release)
    else:
        LOG.info("FAILED: %s", args.release)



class TestServerCommand(cmd.Command):
    def get_parser(self, prog_name):
        parser = super(TestServerCommand, self).get_parser(prog_name)
        parser.add_argument('--release', action='store',
                            default=True, help='Test Armada Manifest')

        return parser

    def take_action(self, parsed_args):
        testService(parsed_args)
