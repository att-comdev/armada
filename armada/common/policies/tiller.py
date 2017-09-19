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


tiller_policies = [
    policy.DocumentedRuleDefault(
        name=base.TILLER % 'get_status',
        check_str=base.RULE_ADMIN_REQUIRED,
        description='Get tiller status',
        operations=[{'path': '/api/v1.0/status/', 'method': 'GET'}]),

    policy.DocumentedRuleDefault(
        name=base.TILLER % 'get_release',
        check_str=base.RULE_ADMIN_REQUIRED,
        description='Get tiller release',
        operations=[{'path': '/api/v1.0/releases/', 'method': 'GET'}]),
]


def list_rules():
    return tiller_policies
