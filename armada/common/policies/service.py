# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_policy import policy

from armada.common.policies import base


armada_policies = [
    policy.DocumentedRuleDefault(
        name=base.ARMADA % 'create_endpoints',
        check_str=base.RULE_ADMIN_REQUIRED,
        description='install manifest charts',
        operations=[{'path': 'api/v1.0/apply/', 'method': 'POST'}]),
    policy.DocumentedRuleDefault(
        name=base.ARMADA % 'validate_manifest',
        check_str=base.RULE_ADMIN_REQUIRED,
        description='validate installed manifest',
        operations=[{'path': '/api/v1.0/validate/', 'method': 'POST'}]),
    policy.DocumentedRuleDefault(
        name=base.ARMADA % 'test_release',
        check_str=base.RULE_ADMIN_REQUIRED,
        description='validate install manifest',
        operations=[{'path': '/api/v1.0/test/{release}', 'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name=base.ARMADA % 'test_manifest',
        check_str=base.RULE_ADMIN_REQUIRED,
        description='validate install manifest',
        operations=[{'path': '/api/v1.0/tests/', 'method': 'POST'}]),
]


def list_rules():
    return armada_policies
