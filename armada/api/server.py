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
#

import sys

from armada.conf import default

default.register_opts()

from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF
CONF(sys.argv[1:])


LOG = logging.getLogger(__name__)

CONF = cfg.CONF
DOMAIN = 'armada'

logging.setup(CONF, DOMAIN)

import falcon

from middleware import AuthMiddleware, ContextMiddleware, LoggingMiddleware

from armada.api.armada_controller import Apply
from armada.api.tiller_controller import Release, Status
from armada.api.validate_controller import Validate
from armada.policy import ArmadaPolicy

from armada.api import ArmadaRequest

def create(middleware=CONF.middleware):
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
