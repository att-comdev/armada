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
import requests
import yaml

from armada.cli import CliAction
from armada.utils.lint import validate_armada_documents
from armada.utils.lint import validate_armada_object
from armada.utils.lint import validate_manifest_url
from armada.utils.lint import validate_manifest_filepath
from armada.handlers.manifest import Manifest


@click.group()
def validate():
    """ Test Manifest Charts

    """


DESC = """
This command validates Armada Manifest

The validate argument must be a relative path to Armada manifest

    $ armada validate examples/simple.yaml

"""

SHORT_DESC = "command validates Armada Manifest"


@validate.command(name='validate', help=DESC, short_help=SHORT_DESC)
@click.argument('filename', nargs=-1)
@click.pass_context
def validate_manifest(ctx, filename):
    ValidateManifest(ctx, filename).invoke()


class ValidateManifest(CliAction):

    def __init__(self, ctx, filename):
        super(ValidateManifest, self).__init__()
        self.ctx = ctx
        self.filename = filename

    def invoke(self):
        if validate_manifest_filepath(self.filename):
            with open(self.filename) as f:
                docs = f.read()
        elif validate_manifest_url(self.filename):
            docs = requests.get(self.filename, '').text
        else:
            raise Exception('Not a valid URL/filepath')

        if not self.ctx.obj.get('api', False):
            try:
                documents = []
                for f in self.filename:
                    doc_data = ReferenceResolver(f)
                    documents.extend(yaml.safe_load_all(doc_data.decode()))
            except InvalidPathException as ex:
                self.logger.error("Not a valid URL/filepath: %s", f)
                return
            except yaml.YAMLError as yex:
                self.logger.error("Invalid YAML found in %s." % f)
                return

            manifest_obj = Manifest(documents).get_manifest()
            obj_check = validate_armada_object(manifest_obj)
            doc_check = validate_armada_documents(documents)

            try:
                if doc_check and obj_check:
                    self.logger.info(
                        'Successfully validated: %s', self.filename)
            except Exception:
                raise Exception('Failed to validate: %s', self.filename)
        else:
            if len(self.filename) > 1:
                self.logger.error("Cannot specify multiple locations when using the API.")
                return

            client = self.ctx.obj.get('CLIENT')
            resp = client.post_validate(self.filename[0])

            if resp.get('code') == 200:
                self.logger.info(
                    'Successfully validated: %s', self.filename[0])
            else:
                self.logger.error("Failed to validate: %s", self.filename[0])
