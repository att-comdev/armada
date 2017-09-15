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


import click
import yaml

from armada.cli import CliAction
from armada.utils.validate import validate_armada_documents


@click.group()
def validate():
    """ Test Manifest Charts

    """


DESC = """
This command validates Armada Manifest

The validate argument must be a relative path to an Armada manifest file.

    $ armada validate examples/simple.yaml

"""

SHORT_DESC = "command validates Armada Manifest"


@validate.command(name='validate', help=DESC, short_help=SHORT_DESC)
@click.argument('filename')
@click.pass_context
def validate_manifest(ctx, filename):
    ValidateManifest(ctx, filename).invoke()


class ValidateManifest(CliAction):

    def __init__(self, ctx, filename):
        super(ValidateManifest, self).__init__()
        self.ctx = ctx
        self.filename = filename

    def invoke(self):
        if not self.ctx.obj.get('api', False):
            with open(self.filename) as f:
                documents = list(yaml.safe_load_all(f.read()))
                error_messages = validate_armada_documents(documents)
                if not error_messages:
                    self.logger.info(
                        'Successfully validated manifest: %s.', self.filename)
                else:
                    self.logger.error('Invalid manifest: %s.', self.filename)
                    for error_message in error_messages:
                        self.logger.error(error_message)
        else:
            client = self.ctx.obj.get('CLIENT')
            with open(self.filename, 'r') as f:
                resp = client.post_validate(f.read())
                if resp.get('valid', False):
                    self.logger.info(
                        'Successfully validated: %s', self.filename)
                else:
                    self.logger.error("Failed to validate manifest: %s.",
                                      self.filename)
                    for error in resp.get('errors', []):
                        self.logger.error(error)
