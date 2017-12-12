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

from armada import conf
from armada.api import ArmadaRequest
from armada.api.controller.armada import Apply
from armada.api.middleware import AuthMiddleware
from armada.api.middleware import ContextMiddleware
from armada.api.middleware import LoggingMiddleware
from armada.api.controller.test import Test
from armada.api.controller.test import Tests
from armada.api.controller.version import Version
from armada.api.controller.tiller import Release
from armada.api.controller.tiller import Status
from armada.api.controller.validation import Validate
from armada.common import policy

conf.set_app_default_configs()
CONF = cfg.CONF


# Build API
def create(middleware=CONF.middleware):

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
    url_routes_v1 = (
        ('apply', Apply()),
        ('releases', Release()),
        ('status', Status()),
        ('tests', Tests()),
        ('test/{release}', Test()),
        ('validate', Validate()),
    )

    api.add_route("/versions", Version())

    for route, service in url_routes_v1:
        api.add_route("/api/v1.0/{}".format(route), service)

    return api


def paste_start_armada(global_conf, **kwargs):
    # At this time just ignore everything in  the paste configuration
    # and rely on olso_config

    return api


api = create()
