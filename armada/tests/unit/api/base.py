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

from falcon import testing as falcon_testing

from armada.api import server
from armada.tests.unit import base as test_base
from armada.tests.unit import fixtures


class BaseControllerTest(test_base.ArmadaTestCase):
    """Base class for unit testing falcon controllers."""

    def setUp(self):
        super(BaseControllerTest, self).setUp()
        self.app = falcon_testing.TestClient(server.create(middleware=False))
        self.policy = self.useFixture(fixtures.RealPolicyFixture())
