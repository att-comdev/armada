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

import os

import click
from oslo_config import cfg
from oslo_log import log
from urlparse import urlparse

from armada.common.client import ArmadaClient
from armada.common.session import ArmadaSession
from armada.cli.apply import apply_create
from armada.cli.test import test_charts
from armada.cli.tiller import tiller_service
from armada.cli.validate import validate_manifest

CONF = cfg.CONF

@click.group()
@click.option(
    '--debug/--no-debug', help='Enable or disable debugging', default=False)
@click.option(
    '--api/--no-api', help='Execute service endpoints. (requires url option)',
    default=False)
@click.option(
    '--url', help='Armada service endpoint', default=None)
@click.option(
    '--token', help='Armada service endpoint', default=None)
@click.option(
    '--os-project-domain-name', help='Armada service endpoint', default=None)
@click.option(
    '--os-user-domain-name', help='Armada service endpoint', default=None)
@click.option(
    '--os-project-name', help='Armada service endpoint', default=None)
@click.option(
    '--os-username', help='Armada service endpoint', default=None)
@click.option(
    '--os-password', help='Armada service endpoint', default=None)
@click.option(
    '--os-auth-url', help='Armada service endpoint', default=None)
@click.option(
    '--os-identity-api-version', help='Armada service endpoint', default='v3')
@click.option(
    '--os-image-api-version', help='Armada service endpoint', default=None)
@click.pass_context
def main(ctx, debug, api, url, token,
         os_project_domain_name,
         os_user_domain_name,
         os_project_name,
         os_username,
         os_password,
         os_auth_url,
         os_identify_api_version,
         os_image_api_version):
    """
    Multi Helm Chart Deployment Manager

    Common actions from this point include:

    $ armada apply
    $ armada test
    $ armada tiller
    $ armada validate

    Environment:

        $TOKEN set auth token
        $HOST  set armada service host endpoint
        $OS_PROJECT_DOMAIN_NAME keystone project domain name
        $OS_USER_DOMAIN_NAME keystone user domain name
        $OS_PROJECT_NAME keystone project name
        $OS_USERNAME keystone service username
        $OS_PASSWORD keystone service password
        $OS_AUTH_URL keystone service endpoint
        $OS_IDENTITY_API_VERSION keystone service endpoint version
        $OS_IMAGE_API_VERSION keystone service image api version

    This tool will communicate with deployed Tiller in your Kubernetes cluster.
    """

    if not ctx.obj:
        ctx.obj = {}

    if api:
        if not url:
            url = os.environ.get('HOST')
        if not token or os.environ.get('TOKEN'):
            token = os.environ.get('TOKEN')
        else:
            if not os_project_domain_name:
                os_project_domain_name = os.environ.get(
                    'os_project_domain_name')
            if not os_user_domain_name:
                os_user_domain_name = os.environ.get('os_user_domain_name')
            if not os_project_name:
                os_project_name = os.environ.get('os_project_name')
            if not os_username:
                os_username = os.environ.get('os_username')
            if not os_password:
                os_password = os.environ.get('os_password')
            if not os_auth_url:
                os_auth_url = os.environ.get('os_project_domain_name')
            if not os_identify_api_version:
                os_identify_api_version = os.environ.get(
                    'os_identify_api_version')
            if not os_image_api_version:
                os_image_api_version = os.environ.get('os_image_api_version')

        ctx.obj['api'] = api
        if url:
            parsed_url = urlparse(url)
            ctx.obj['CLIENT'] = ArmadaClient(
                ArmadaSession(
                    host=parsed_url.netloc,
                    scheme=parsed_url.scheme,
                    token=token)
            )
        else:
            raise Exception(
                'When api option is enable user needs to pass url')

    log.register_options(CONF)

    if debug:
        CONF.debug = debug

    log.set_defaults(default_log_levels=CONF.default_log_levels)
    log.setup(CONF, 'armada')


main.add_command(apply_create)
main.add_command(test_charts)
main.add_command(tiller_service)
main.add_command(validate_manifest)
