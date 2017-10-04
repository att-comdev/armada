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

import click

from armada.cli import CliAction
from armada import const
from armada.handlers.manifest import Manifest
from armada.handlers.tiller import Tiller
from armada.utils.release import release_prefix


@click.group()
def test():
    """ Test Manifest Charts

    """


DESC = """
This command test deployed charts

The tiller command uses flags to obtain information from tiller services.
The test command will run the release chart tests either via a the manifest or
by targetings a relase.

To test armada deployed releases:

    $ armada test --file examples/simple.yaml

To test release:

    $ armada test --release blog-1

"""

SHORT_DESC = "command test releases"


@test.command(name='test', help=DESC, short_help=SHORT_DESC)
@click.option('--file', help='armada manifest', type=str)
@click.option('--output', help='pod output log', is_flag=True)
@click.option('--release', help='helm release', type=str)
@click.option('--tiller-host', help="Tiller Host IP")
@click.option(
    '--tiller-port', help="Tiller host Port", type=int, default=44134)
@click.pass_context
def test_charts(ctx, file, output, release, tiller_host, tiller_port):
    TestChartManifest(
        ctx, file, output, release, tiller_host, tiller_port).invoke()


class TestChartManifest(CliAction):
    def __init__(self, ctx, file, output, release, tiller_host, tiller_port):

        super(TestChartManifest, self).__init__()
        self.ctx = ctx
        self.file = file
        self.output = output
        self.release = release
        self.tiller_host = tiller_host
        self.tiller_port = tiller_port

    def output_release(self, resp, output=False):
        if output:
            self.logger.info(resp.get('output', ''))

        for k, v in resp.get('status').items():
            self.logger.info("Test %s: %s", k, v)

    def invoke(self):
        tiller = Tiller(
            tiller_host=self.tiller_host, tiller_port=self.tiller_port)
        known_release_names = [release[0] for release in tiller.list_charts()]

        if self.release:
            if not self.ctx.obj.get('api', False):
                resp = tiller.testing_release(
                    self.release, output=self.output)
                self.output_release(resp, self.output)

                # {'output': podlogs, 'status':{'release': p/f/s}}
            else:
                client = self.ctx.obj.get('CLIENT')
                query = {
                    'output': self.output,
                    'tiller_host': self.tiller_host,
                    'tiller_port': self.tiller_port
                }
                resp = client.get_test_release(release=self.release,
                                               query=query)
                self.output_release(resp, self.output)

        if self.file:
            if not self.ctx.obj.get('api', False):
                documents = yaml.safe_load_all(open(self.file).read())
                armada_obj = Manifest(documents).get_manifest()
                prefix = armada_obj.get(const.KEYWORD_ARMADA).get(
                    const.KEYWORD_PREFIX)

                for group in armada_obj.get(const.KEYWORD_ARMADA).get(
                        const.KEYWORD_GROUPS):
                    for ch in group.get(const.KEYWORD_CHARTS):
                        release_name = release_prefix(
                            prefix, ch.get('chart').get('chart_name'))

                        output = self.output
                        if not output:
                            output = ch.get('chart').get('test', {}).get(
                                'output', False)

                        if release_name in known_release_names:
                            self.logger.info('RUNNING: %s tests', release_name)
                            resp = tiller.testing_release(release_name, output)

                            self.output_release(resp, output=output)

                        else:
                            self.logger.info(
                                'Release %s not found - SKIPPING',
                                release_name)
            else:
                client = self.ctx.obj.get('CLIENT')
                query = {
                    'output': self.output,
                    'tiller_host': self.tiller_host,
                    'tiller_port': self.tiller_port
                }

                with open(self.file, 'r') as f:
                    resp = client.post_test_manifest(manifest=f.read(),
                                                     query=query)
                    for result in resp.get('results', ''):
                        self.output_release(result, self.output)

                    if resp.get('info', ''):
                        self.logger.info(resp['info'])
