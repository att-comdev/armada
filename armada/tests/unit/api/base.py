# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
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

import os

from falcon import testing as falcon_testing
import mock

from armada.api import server
import armada.conf
from armada.tests.unit import base as test_base
from armada.tests.unit import fixtures


class BaseControllerTest(test_base.ArmadaTestCase):
    """Base class for unit testing falcon controllers."""

    def setUp(self):
        super(BaseControllerTest, self).setUp()
        # Override the default configuration file lookup with references to
        # the sample configuration files to avoid oslo.conf errors when
        # creating the server below.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        sample_conf_dir = os.path.join(current_dir, os.pardir, os.pardir,
                                       os.pardir, os.pardir, 'etc', 'armada')
        sample_conf_files = ['api-paste.ini', 'armada.conf.sample']
        with mock.patch.object(
                armada.conf, '_get_config_files') as mock_get_config_files:
            mock_get_config_files.return_value = [
                os.path.join(sample_conf_dir, x) for x in sample_conf_files
            ]
            self.app = falcon_testing.TestClient(
                server.create(enable_middleware=False))
        self.policy = self.useFixture(fixtures.RealPolicyFixture())
