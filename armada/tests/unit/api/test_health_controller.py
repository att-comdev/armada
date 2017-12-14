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

import falcon

from armada.tests.unit.api import base


class HealthControllerTest(base.BaseControllerTest):

    def test_get_health_status(self):
        """
        Validate that /api/v1.0/health returns 204.
        """
        result = self.app.simulate_get('/api/v1.0/health')
        self.assertEqual(result.status, falcon.HTTP_204)
