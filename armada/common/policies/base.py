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

ARMADA = 'armada:%s'
TILLER = 'tiller:%s'
RULE_ADMIN_REQUIRED = 'rule:admin_required'
RULE_ADMIN_OR_TARGET_PROJECT = (
    'rule:admin_required or project_id:%(target.project.id)s')
RULE_SERVICE_OR_ADMIN = 'rule:service_or_admin'


rules = [
    policy.RuleDefault(name='admin_required',
                       check_str='role:admin or is_admin:1'),
    policy.RuleDefault(name='service_or_admin',
                       check_str='rule:admin_required or rule:service_role'),
    policy.RuleDefault(name='service_role',
                       check_str='role:service'),
]


def list_rules():
    return rules
