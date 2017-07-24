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
import sys

from oslo_config import cfg
from oslo_log import log as logging

from armada import conf
from armada.api import ArmadaRequest
from armada.api.armada_controller import Apply
from armada.api.tiller_controller import Release
from armada.api.tiller_controller import Status
from armada.api.validate_controller import Validate
from armada.policy import ArmadaPolicy
from middleware import AuthMiddleware
from middleware import ContextMiddleware
from middleware import LoggingMiddleware


CONF = cfg.CONF
CONF(sys.argv[1:])

LOG = logging.getLogger(__name__)
conf.set_app_default_configs()


def create(middleware=CONF.middleware):
    logging.register_options(CONF)
    logging.set_defaults(default_log_levels=CONF.default_log_levels)
    logging.setup(CONF, 'armada')

    if middleware:
        api = falcon.API(
            request_type=ArmadaRequest,
            middleware=[
                AuthMiddleware(),
                ContextMiddleware(),
                LoggingMiddleware()
            ])
    else:
        api = falcon.API()

    # Authencitcation Policy
    policy_engine = ArmadaPolicy(CONF)
    policy_engine.register_policy()

    # Define serives Routes v1.0
    url_routes_v1 = (
        ('status', Status(policy_engine=policy_engine)),
        ('releases', Release(policy_engine=policy_engine)),
        ('validate', Validate(policy_engine=policy_engine)),
        ('apply', Apply(policy_engine=policy_engine))
    )

    for route, service in url_routes_v1:
        api.add_route('/v1.0/{}'.format(route), service)

    return api

def paste_start_armada(global_conf, **kwargs):
        # At this time just ignore everything in the paste configuration
        # and rely on oslo_config

        return api


api = create()
