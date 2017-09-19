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

from armada.cli import CliAction
from armada.handlers.tiller import Tiller


@click.group()
def tiller():
    """ Tiller Services actions

    """


DESC = """
This command gets tiller information

The tiller command uses flags to obtain information from tiller services

To obtain armada deployed releases:

    $ armada tiller --releases

To obtain tiller service status/information:

    $ armada tiller --status

"""

SHORT_DESC = "command gets tiller infromation"


@tiller.command(name='tiller', help=DESC, short_help=SHORT_DESC)
@click.option('--tiller-host', help="Tiller host ip", default=None)
@click.option(
    '--tiller-port', help="Tiller host port", type=int, default=44134)
@click.option('--releases', help="list of deployed releses", is_flag=True)
@click.option('--status', help="Status of Armada services", is_flag=True)
@click.pass_context
def tiller_service(ctx, tiller_host, tiller_port, releases, status):
    TillerServices(ctx, tiller_host, tiller_port, releases, status).invoke()


class TillerServices(CliAction):

    def __init__(self, ctx, tiller_host, tiller_port, releases, status):
        super(TillerServices, self).__init__()
        self.ctx = ctx
        self.tiller_host = tiller_host
        self.tiller_port = tiller_port
        self.releases = releases
        self.status = status

    def invoke(self):

        tiller = Tiller(
            tiller_host=self.tiller_host, tiller_port=self.tiller_port)

        if self.status:
            if not self.ctx.obj.get('api', False):
                resp = tiller.tiller_version()
                self.logger.info('Tiller Service: %s', tiller.tiller_status())
                self.logger.info(
                    'Tiller Version: %s',
                    getattr(resp.Version, 'sem_ver', False))
            else:
                client = self.ctx.obj.get('CLIENT')
                resp = client.get_status()
                tiller_status = resp.get('tiller').get('state', False)
                tiller_version = resp.get('tiller').get('version')

                self.logger.info("Tiller Service: %s", tiller_status)
                self.logger.info("Tiller Version: %s", tiller_version)

        if self.releases:
            if not self.ctx.obj.get('api', False):
                for release in tiller.list_releases():
                    self.logger.info(
                        "Release %s in namespace: %s",
                        release.name, release.namespace)
            else:
                client = self.ctx.obj.get('CLIENT')
                resp = client.get_releases()
                for namespace in resp.get('releases'):
                    for release in resp.get('releases').get(namespace):
                        self.logger.info(
                            'Release %s in namespace: %s', release,
                            namespace)
