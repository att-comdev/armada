# Copyright 2017 The Armada Authors.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import importlib
import os

from falcon import testing as falcon_testing
import mock

import armada.conf
from armada.tests.unit import base as test_base
from armada.tests.unit import fixtures


class BaseControllerTest(test_base.ArmadaTestCase):
    """Base class for unit testing falcon controllers."""

    def setUp(self):
        super(BaseControllerTest, self).setUp()
        # Override the default configuration file lookup with references to
        # the sample configuration files to avoid oslo.conf errors when
        # the server below.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        sample_conf_dir = os.path.join(current_dir, os.pardir, os.pardir,
                                       os.pardir, os.pardir, 'etc', 'armada')
        sample_conf_files = ['armada.conf.sample', 'api-paste.ini']
        with mock.patch.object(
                armada.conf, '_get_config_files') as mock_get_config_files:
            mock_get_config_files.return_value = [
                os.path.join(sample_conf_dir, x) for x in sample_conf_files
            ]
            # FIXME(fmontei): Workaround for the fact that `armada.api` always
            # calls `create()` via `api = create()` at the bottom of the module
            # which invokes oslo.conf functionality that has yet to be set up
            # properly in this module.
            server = importlib.import_module('armada.api.server')
            self.app = falcon_testing.TestClient(
                server.create(enable_middleware=False))
        self.policy = self.useFixture(fixtures.RealPolicyFixture())
