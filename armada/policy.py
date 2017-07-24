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


from oslo_config import cfg
from oslo_policy import policy


class ArmadaPolicy(object):
    '''
    Init policy defaults
    '''

    base_rules = [
        policy.RuleDefault(
            'admin_required',
            'role:admin or is_admin:1',
            description='Actions requiring admin auth')
    ]

    task_rules = [
        policy.RuleDefault(
            'chart_installer:validate',
            'role:admin', description='Validate Manifest'),
        policy.RuleDefault(
            'chart_installer:install',
            'role:admin', description='Installs Manifest charts'),
        policy.RuleDefault(
            'chart_installer:read_releases',
            'role:admin', description='Read Deployed Releases'),
        policy.RuleDefault(
            'chart_installer:query_status',
            'role:admin', description='Check status of armada services'),
    ]

    def __init__(self, CONF=cfg.CONF):
        self.enforcer = policy.Enforcer(CONF)

    def register_policy(self):
        self.enforcer.register_defaults(ArmadaPolicy.base_rules)
        self.enforcer.register_defaults(ArmadaPolicy.task_rules)
        self.enforcer.load_rules()

    def authorize(self, action, ctx):
        target = {'project_id': ctx.project_id, 'user_id': ctx.user_id}

        return self.enforcer.authorize(action, target, ctx.to_policy_view())

def list_policies():
    default_policy = []
    default_policy.extend(ArmadaPolicy.base_rules)
    default_policy.extend(ArmadaPolicy.task_rules)

    return default_policy
