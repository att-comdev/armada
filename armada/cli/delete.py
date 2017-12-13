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
def delete():
    """ Delete releases by release name Or manifest file

    """

DESC = """
This command delete releases.

The delete command will delete the releases either via a manifest
or by targetings a release.

To delete all the releases that are created by the armada manifest :

    $ armada delete --manifest examples/simple.yaml

To delete releases by the name:

    $ armada delete --release blog-1

    or

    $ armada delete --release blog-1,blog-2,blog-3

"""

SHORT_DESC = "command delete releases"

@delete.command(name='delete', help=DESC, short_help=SHORT_DESC)
@click.option('--manifest', help='armada manifest file', type=str)
@click.option('--release', help='helm release name', type=str)
@click.option(
    '--no-purge', help="delete release without purge option", is_flag=True)
@click.option('--tiller-host', help="Tiller Host IP")
@click.option(
    '--tiller-port', help="Tiller host Port", type=int, default=44134)
@click.pass_context
def delete_charts(ctx, manifest, release, no_purge, tiller_host, tiller_port):
    DeleteChartManifest(
        ctx, manifest, release, no_purge, tiller_host, tiller_port).invoke()

class DeleteChartManifest(CliAction):
    def __init__(self, ctx, manifest, release, no_purge, tiller_host,
                 tiller_port):

        super(DeleteChartManifest, self).__init__()
        self.ctx = ctx
        self.manifest = manifest
        self.release = release
        self.purge = not no_purge
        self.tiller_host = tiller_host
        self.tiller_port = tiller_port

    def invoke(self):
        tiller = Tiller(
            tiller_host=self.tiller_host, tiller_port=self.tiller_port)
        known_release_names = [release[0] for release in tiller.list_charts()]
        if self.release:
            releases = self.release.split(',')
            if not self.ctx.obj.get('api', False):
                for release_name in releases:
                    if release_name in known_release_names:
                        self.logger.info("Deleting release %s", release_name)
                        tiller.uninstall_release(release_name, purge=self.purge)

            else:
                client = self.ctx.obj.get('CLIENT')
                query = {
                    'tiller_host': self.tiller_host,
                    'tiller_port': self.tiller_port
                }
                #resp = client.uninstall_release(release=self.release,
                #                                query=query)

                #self.logger.info(resp.get('result'))
                #self.logger.info(resp.get('message'))

        if self.manifest:
            if not self.ctx.obj.get('api', False):
                documents = yaml.safe_load_all(open(self.manifest).read())
                armada_obj = Manifest(documents).get_manifest()
                prefix = armada_obj.get(const.KEYWORD_ARMADA).get(
                    const.KEYWORD_PREFIX)

                for group in armada_obj.get(const.KEYWORD_ARMADA).get(
                        const.KEYWORD_GROUPS):
                    for ch in group.get(const.KEYWORD_CHARTS):
                        release_name = release_prefix(
                            prefix, ch.get('chart').get('chart_name'))
                        if release_name in known_release_names:
                            self.logger.info("Deleting release %s", release_name)
                            tiller.uninstall_release(release_name, purge=self.purge)
            else:
                client = self.ctx.obj.get('CLIENT')
                query = {
                    'tiller_host': self.tiller_host,
                    'tiller_port': self.tiller_port
                }

                with open(self.manifest, 'r') as f:
                    resp = client.get_test_manifest(manifest=f.read(),
                                                    query=query)
                    for test in resp.get('tests'):
                        self.logger.info('Test State: %s', test)
                        for item in test.get('tests').get(test):
                            self.logger.info(item)

                    self.logger.info(resp)
