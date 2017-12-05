# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2017 AT&T Intellectual Property.
# All Rights Reserved.
#
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

"""Fixtures for Armada tests."""
from __future__ import absolute_import

import os
import yaml

import fixtures
import mock
from oslo_config import cfg
from oslo_policy import opts as policy_opts
from oslo_policy import policy as oslo_policy

from armada.common import policies
import armada.common.policy
from armada.tests.unit import fake_policy

CONF = cfg.CONF


class ConfPatcher(fixtures.Fixture):
    """Fixture to patch and restore global CONF.

    This also resets overrides for everything that is patched during
    it's teardown.

    """

    def __init__(self, **kwargs):
        """Constructor

        :params group: if specified all config options apply to that group.

        :params **kwargs: the rest of the kwargs are processed as a
        set of key/value pairs to be set as configuration override.

        """
        super(ConfPatcher, self).__init__()
        self.group = kwargs.pop('group', None)
        self.args = kwargs

    def setUp(self):
        super(ConfPatcher, self).setUp()
        for k, v in self.args.items():
            self.addCleanup(CONF.clear_override, k, self.group)
            CONF.set_override(k, v, self.group)


class RealPolicyFixture(fixtures.Fixture):
    """Load the live policy for tests.

    A base policy fixture that starts with the assumption that you'd
    like to load and enforce the shipped default policy in tests.

    """

    def __init__(self, verify=True, *args, **kwargs):
        """Constructor for ``RealPolicyFixture``.

        :param verify: Whether to verify that expected and actual policies
            match. True by default.
        """
        super(RealPolicyFixture, self).__init__(*args, **kwargs)
        self.verify = verify

    def _setUp(self):
        super(RealPolicyFixture, self)._setUp()
        self.policy_dir = self.useFixture(fixtures.TempDir())
        self.policy_file = os.path.join(self.policy_dir.path,
                                        'policy.yaml')
        # Load the fake_policy data and add the missing default rules.
        policy_rules = yaml.safe_load(fake_policy.policy_data)
        self.add_missing_default_rules(policy_rules)
        with open(self.policy_file, 'w') as f:
            yaml.safe_dump(policy_rules, f)

        policy_opts.set_defaults(CONF)
        self.useFixture(
            ConfPatcher(policy_dirs=[], policy_file=self.policy_file,
                        group='oslo_policy'))

        armada.common.policy.reset_policy()
        armada.common.policy.setup_policy()
        self.addCleanup(armada.common.policy.reset_policy)

        if self.verify:
            self._install_policy_verification_hook()

    def _verify_policies_match(self):
        """Validate that the expected and actual policies are equivalent.
        Otherwise an ``AssertionError`` is raised.
        """
        if not (set(self.expected_policy_actions) ==
                set(self.actual_policy_actions)):
            error_msg = (
                'The expected policy actions passed to '
                '`self.policy.set_rules` do not match the policy actions '
                'that were actually enforced by Armada. Set of expected '
                'policies %s should be equal to set of actual policies: %s. '
                'There is either a bug with the test or with policy '
                'enforcement in the controller.' % (
                    self.expected_policy_actions,
                    self.actual_policy_actions)
            )
            raise AssertionError(error_msg)

    def _install_policy_verification_hook(self):
        """Install policy verification hook for validating RBAC.

        This function's purpose is to guarantee that policy enforcement is
        happening the way we expect it to. It validates that the policies
        that are passed to ``self.policy.set_rules`` from within a test that
        uses this fixture is a subset of the actual policies that are enforced
        by Armada controllers.

        The algorithm is as follows:

            1) Initialize list of actual policy actions to remember.
            2) Initialize list of expected policy actions to remember.
            3) Reference a pre-mocked copy of the policy enforcement function
               that is ultimately called by Armada for policy enforcement.
            4a) Create a hook that stores the actual policy for later.
            4b) The hook then calls the *real* policy enforcement function
                using the reference from step 3).
            5) Mock the policy enforcement function and have it instead call
               our hook from step 4a).
            6) Add a clean up to undo the mock from step 5).

        There is a tight coupling between this function and ``set_rules``
        below.

        The comparison between ``self.expected_policy_actions`` and
        ``self.actual_policy_actions`` is performed during clean up.
        """
        self.actual_policy_actions = []
        self.expected_policy_actions = []
        _do_enforce_rbac = armada.common.policy._enforce_policy

        def enforce_policy_and_remember_actual_rules(
                action, *a, **k):
            self.actual_policy_actions.append(action)
            _do_enforce_rbac(action, *a, **k)

        mock_do_enforce_rbac = mock.patch.object(
            armada.common.policy, '_enforce_policy', autospec=True).start()
        mock_do_enforce_rbac.side_effect = (
            enforce_policy_and_remember_actual_rules)
        self.addCleanup(mock.patch.stopall)
        self.addCleanup(self._verify_policies_match)

    def add_missing_default_rules(self, rules):
        """Adds default rules and their values to the given rules dict.

        The given rulen dict may have an incomplete set of policy rules.
        This method will add the default policy rules and their values to
        the dict. It will not override the existing rules.
        """
        for rule in policies.list_rules():
            if rule.name not in rules:
                rules[rule.name] = rule.check_str

    def set_rules(self, rules, overwrite=True):
        """Set the custom policy rules to override.

        :param dict rules: Dictionary keyed with policy actions enforced
            by Armada whose values are a custom rule understood by
            ``oslo.policy`` library.

        This function overrides the default policy rules with the custom rules
        specified by ``rules``. The ``rules`` passed here are added to
        ``self.expected_policy_actions`` for later comparison with
        ``self.actual_policy_actions``.
        """
        if isinstance(rules, dict):
            rules = oslo_policy.Rules.from_dict(rules)

        self.expected_policy_actions.extend(rules)

        policy = armada.common.policy._ENFORCER
        policy.set_rules(rules, overwrite=overwrite)
