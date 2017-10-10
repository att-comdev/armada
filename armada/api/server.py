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

import falcon
from oslo_config import cfg
from oslo_log import log as logging

from armada import conf
from armada.api import ArmadaRequest
from armada.api.armada_controller import Apply
from armada.api.middleware import AuthMiddleware
from armada.api.middleware import ContextMiddleware
from armada.api.middleware import LoggingMiddleware
from armada.api.tiller_controller import Release
from armada.api.tiller_controller import Status
from armada.api.validation_controller import Validate
from armada.common import policy

LOG = logging.getLogger(__name__)
conf.set_app_default_configs()
CONF = cfg.CONF


# Build API
def create(middleware=CONF.middleware):
    if not (os.path.exists('etc/armada/armada.conf')):
        logging.register_options(CONF)
        logging.set_defaults(default_log_levels=CONF.default_log_levels)
        logging.setup(CONF, 'armada')

    policy.setup_policy()

    if middleware:
        api = falcon.API(
            request_type=ArmadaRequest,
            middleware=[
                AuthMiddleware(),
                LoggingMiddleware(),
                ContextMiddleware()
            ])
    else:
        api = falcon.API(request_type=ArmadaRequest)

    # Configure API routing
    url_routes_v1 = (('apply', Apply()),
                     ('releases', Release()),
                     ('status', Status()),
                     ('validate', Validate()))

    for route, service in url_routes_v1:
        api.add_route("/v1.0/{}".format(route), service)

    return api


def paste_start_armada(global_conf, **kwargs):
    # At this time just ignore everything in  the paste configuration
    # and rely on olso_config

    return api


api = create()
