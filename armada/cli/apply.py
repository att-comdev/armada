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
from oslo_config import cfg

from armada.cli import CliAction
from armada.exceptions.source_exceptions import InvalidPathException
from armada.handlers.armada import Armada
from armada.handlers.document import ReferenceResolver

CONF = cfg.CONF


@click.group()
def apply():
    """ Apply manifest to cluster

    """


DESC = """
This command install and updates charts defined in armada manifest

The apply argument must be relative path to Armada Manifest. Executing apply
commnad once will install all charts defined in manifest. Re-executing apply
commnad will execute upgrade.

To see how to create an Armada manifest:
    http://armada-helm.readthedocs.io/en/latest/operations/

To obtain install/upgrade charts:

    \b
    $ armada apply examples/simple.yaml

To obtain override manifest:

    \b
    $ armada apply examples/simple.yaml \
--set manifest:simple-armada:relase_name="wordpress"

    \b
    or

    \b
    $ armada apply examples/simple.yaml \
--values examples/simple-ovr-values.yaml

"""

SHORT_DESC = "command install manifest charts"


@apply.command(name='apply', help=DESC, short_help=SHORT_DESC)
@click.argument('locations', nargs=-1)
@click.option('--api', help="Contacts service endpoint", is_flag=True)
@click.option(
    '--disable-update-post', help="run charts without install", is_flag=True)
@click.option(
    '--disable-update-pre', help="run charts without install", is_flag=True)
@click.option('--dry-run', help="run charts without install", is_flag=True)
@click.option(
    '--enable-chart-cleanup', help="Clean up Unmanaged Charts", is_flag=True)
@click.option('--set', multiple=True, type=str, default=[])
@click.option('--tiller-host', help="Tiller host ip")
@click.option(
    '--tiller-port', help="Tiller host port", type=int, default=44134)
@click.option(
    '--timeout',
    help="specifies time to wait for charts",
    type=int,
    default=3600)
@click.option('--values', '-f', multiple=True, type=str, default=[])
@click.option('--wait', help="wait until all charts deployed", is_flag=True)
@click.option(
    '--debug/--no-debug', help='Enable or disable debugging', default=False)
@click.pass_context
def apply_create(ctx, locations, api, disable_update_post, disable_update_pre,
                 dry_run, enable_chart_cleanup, set, tiller_host, tiller_port,
                 timeout, values, wait, debug):

    if debug:
        CONF.debug = debug

    ApplyManifest(ctx, locations, api, disable_update_post, disable_update_pre,
                  dry_run, enable_chart_cleanup, set, tiller_host, tiller_port,
                  timeout, values, wait).invoke()


class ApplyManifest(CliAction):
    def __init__(self, ctx, locations, api, disable_update_post,
                 disable_update_pre, dry_run, enable_chart_cleanup, set,
                 tiller_host, tiller_port, timeout, values, wait):
        super(ApplyManifest, self).__init__()
        self.ctx = ctx
        # Filename can also be a URL reference
        self.locations = locations
        self.api = api
        self.disable_update_post = disable_update_post
        self.disable_update_pre = disable_update_pre
        self.dry_run = dry_run
        self.enable_chart_cleanup = enable_chart_cleanup
        self.set = set
        self.tiller_host = tiller_host
        self.tiller_port = tiller_port
        self.timeout = timeout
        self.values = values
        self.wait = wait

    def output(self, resp):
        for result in resp:
            if not resp[result] and not result == 'diff':
                self.logger.info('Did not performed chart %s(s)', result)
            elif result == 'diff' and not resp[result]:
                self.logger.info('No Relase changes detected')

            for ch in resp[result]:
                if not result == 'diff':
                    msg = 'Chart {} was {}'.format(ch, result)
                    self.logger.info(msg)
                else:
                    self.logger.info('Chart values diff')
                    self.logger.info(ch)

    def invoke(self):
        if not self.ctx.obj.get('api', False):
            try:
                doc_data = ReferenceResolver.resolve_reference(self.locations)
                documents = list()
                for d in doc_data:
                    documents.extend(list(yaml.safe_load_all(d.decode())))
            except InvalidPathException as ex:
                self.logger.error(str(ex))
                return
            except yaml.YAMLError as yex:
                self.logger.error("Invalid YAML found: %s" % str(yex))
                return

            armada = Armada(
                documents, self.disable_update_pre, self.disable_update_post,
                self.enable_chart_cleanup, self.dry_run, self.set, self.wait,
                self.timeout, self.tiller_host, self.tiller_port, self.values)

            resp = armada.sync()
            self.output(resp)
        else:
            if len(self.values) > 0:
                self.logger.error(
                    "Cannot specify local values files when using the API.")
                return

            query = {
                'disable_update_post': self.disable_update_post,
                'disable_update_pre': self.disable_update_pre,
                'dry_run': self.dry_run,
                'enable_chart_cleanup': self.enable_chart_cleanup,
                'tiller_host': self.tiller_host,
                'tiller_port': self.tiller_port,
                'timeout': self.timeout,
                'wait': self.wait
            }

            client = self.ctx.obj.get('CLIENT')

            resp = client.post_apply(
                manifest_ref=self.locations, set=self.set, query=query)
            self.output(resp.get('message'))
