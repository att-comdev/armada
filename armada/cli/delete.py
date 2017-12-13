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
    """ Delete releases by targeting specific releases or via a manifest file.

    """


DESC = """
This command deletes releases.

The delete command will delete the releases either via a manifest
or by targeting specific releases.

To delete all the releases that are created by the armada manifest:

    $ armada delete --manifest examples/simple.yaml

To delete releases by the name:

    $ armada delete --releases blog-1

    or

    $ armada delete --releases blog-1,blog-2,blog-3

"""

SHORT_DESC = "command delete releases"


@delete.command(name='delete', help=DESC, short_help=SHORT_DESC)
@click.option('--manifest', help='Armada manifest file', type=str)
@click.option(
    '--releases', help='Comma-separated list of release names', type=str)
@click.option(
    '--no-purge', help="Deletes release without purge option", is_flag=True)
@click.option('--tiller-host', help="Tiller Host IP")
@click.option(
    '--tiller-port', help="Tiller host Port", type=int, default=44134)
@click.pass_context
def delete_charts(ctx, manifest, releases, no_purge, tiller_host, tiller_port):
    DeleteChartManifest(
        ctx, manifest, releases, no_purge, tiller_host, tiller_port).invoke()


class DeleteChartManifest(CliAction):
    def __init__(self, ctx, manifest, releases, no_purge, tiller_host,
                 tiller_port):

        super(DeleteChartManifest, self).__init__()
        self.ctx = ctx
        self.manifest = manifest
        self.releases = releases
        self.purge = not no_purge
        self.tiller_host = tiller_host
        self.tiller_port = tiller_port

    def invoke(self):
        tiller = Tiller(
            tiller_host=self.tiller_host, tiller_port=self.tiller_port)
        known_release_names = [release[0] for release in tiller.list_charts()]

        if self.releases:
            target_releases = [r.strip() for r in self.releases.split(',')
                               if r.strip() in known_release_names]
            if not target_releases:
                self.logger.info("There's no release to delete.")
                return

            if not self.ctx.obj.get('api', False):
                for r in target_releases:
                    self.logger.info("Deleting release %s", r)
                    tiller.uninstall_release(r, purge=self.purge)

            else:
                raise NotImplementedError()

        if self.manifest:
            target_releases = []

            with open(self.manifest) as f:
                documents = yaml.safe_load_all(f.read())
            try:
                armada_obj = Manifest(documents).get_manifest()
                prefix = armada_obj.get(const.KEYWORD_ARMADA).get(
                    const.KEYWORD_PREFIX)

                for group in armada_obj.get(const.KEYWORD_ARMADA).get(
                        const.KEYWORD_GROUPS):
                    for ch in group.get(const.KEYWORD_CHARTS):
                        release_name = release_prefix(
                            prefix, ch.get('chart').get('chart_name'))
                        if release_name in known_release_names:
                            target_releases.append(release_name)
            except yaml.YAMLError as e:
                mark = e.problem_mark
                self.logger.info("While parsing the manifest file, %s. "
                                 "Error position: (%s:%s)", e.problem,
                                 mark.line + 1, mark.column + 1)

            if not target_releases:
                self.logger.info("There's no release to delete.")
                return

            if not self.ctx.obj.get('api', False):
                for r in target_releases:
                    self.logger.info("Deleting release %s", r)
                    tiller.uninstall_release(r, purge=self.purge)

            else:
                raise NotImplementedError()
