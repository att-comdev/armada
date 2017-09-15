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
from armada.utils.validate import validate_armada_manifest
from armada.handlers.manifest import Manifest
from armada.handlers.document import ReferenceResolver


@click.group()
def validate():
    """ Test Manifest Charts

    """


DESC = """
This command validates an Armada Manifest.

The validate argument must be a relative path to Armada manifest

    $ armada validate examples/simple.yaml

"""

SHORT_DESC = "Command validates Armada Manifest."


@validate.command(name='validate',
                  help=DESC,
                  short_help=SHORT_DESC)
@click.argument('locations',
                nargs=-1)
@click.pass_context
def validate_manifest(ctx, locations):
    ValidateManifest(ctx, locations).invoke()


class ValidateManifest(CliAction):
    def __init__(self, ctx, locations):
        super(ValidateManifest, self).__init__()
        self.ctx = ctx
        self.locations = locations

    def invoke(self):
        if not self.ctx.obj.get('api', False):
            doc_data = ReferenceResolver.resolve_reference(self.locations)
            documents = list()
            for d in doc_data:
                documents.extend(list(yaml.safe_load_all(d.decode())))

            manifest_obj = Manifest(documents).get_manifest()
            obj_check = validate_armada_manifest(manifest_obj)
            doc_check = validate_armada_documents(documents)

            try:
                if doc_check and obj_check:
                    self.logger.info('Successfully validated: %s',
                                     self.locations)
            except Exception:
                raise Exception('Failed to validate: %s', self.locations)
        else:
            if len(self.locations) > 1:
                self.logger.error(
                    "Cannot specify multiple locations "
                    "when using validate API."
                )
                return

            client = self.ctx.obj.get('CLIENT')
            resp = client.post_validate(self.locations[0])

            if resp.get('code') == 200:
                self.logger.info('Successfully validated: %s', self.locations)
            else:
                self.logger.error("Failed to validate: %s", self.locations)
