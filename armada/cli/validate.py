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

from armada.utils.lint import valid_manifest

from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
DOMAIN = "armada"

logging.setup(CONF, DOMAIN)


def validateYaml(args):
    config = yaml.load(open(args.file).read())
    if valid_manifest(config):
        LOG.info('File successfully validated')


class ValidateYamlCommand(cmd.Command):
    def get_parser(self, prog_name):
        parser = super(ValidateYamlCommand, self).get_parser(prog_name)
        parser.add_argument(
            'file',
            type=str,
            metavar='FILE',
            help='Armada yaml file to validate')
        return parser

    def take_action(self, parsed_args):
        validateYaml(parsed_args)
