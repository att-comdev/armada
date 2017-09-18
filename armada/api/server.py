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

import falcon

from oslo_config import cfg
from oslo_log import log as logging

import armada.conf as configs

from .armada_controller import Apply
from .middleware import AuthMiddleware
from .middleware import RoleMiddleware
from .tiller_controller import Release
from .tiller_controller import Status

LOG = logging.getLogger(__name__)
configs.set_app_default_configs()
CONF = cfg.CONF

# Build API
def create(middleware=CONF.middleware):
    logging.register_options(CONF)
    logging.set_defaults(default_log_levels=CONF.default_log_levels)
    logging.setup(CONF, 'armada')

    if middleware:
        api = falcon.API(middleware=[AuthMiddleware(), RoleMiddleware()])
    else:
        api = falcon.API()

    # Configure API routing
    url_routes = (
        ('/tiller/status', Status()),
        ('/tiller/releases', Release()),
        ('/armada/apply/', Apply())
    )

    for route, service in url_routes:
        api.add_route(route, service)

    return api


api = create()
