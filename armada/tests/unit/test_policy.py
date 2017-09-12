#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import testtools

from oslo_policy import policy as common_policy

from armada.common import policy
from armada import conf as cfg
from armada.exceptions import base_exception as exc


CONF = cfg.CONF


class PolicyTestCase(testtools.TestCase):

    def setUp(self):
        super(PolicyTestCase, self).setUp()
        self.rules = {
            "true": [],
            "example:allowed": [],
            "example:disallowed": [["false:false"]],
        }
        self._set_rules()
        self.credentials = {}
        self.target = {}

    def _set_rules(self):
        curr_rules = common_policy.Rules.from_dict(self.rules)
        policy._ENFORCER.set_rules(curr_rules)

    def test_enforce_nonexistent_action(self):
        action = "example:nope"
        self.assertRaises(exc.ActionForbidden, policy.enforce_policy,
                          action, self.target, self.credentials)

    def test_enforce_good_action(self):
        action = "example:allowed"
        policy.enforce_policy(action, self.target, self.credentials)

    def test_enforce_bad_action(self):
        action = "example:disallowed"
        self.assertRaises(exc.ActionForbidden, policy.enforce_policy,
                          action, self.target, self.credentials)
