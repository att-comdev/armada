# Copyright 2013 IBM Corp.
# Copyright 2017 AT&T Intellectual Property.
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

from __future__ import absolute_import

import socket

import fixtures
import mock
from oslo_config import cfg
import testtools

from armada.conf import default

CONF = cfg.CONF


def is_connected():
    """Verifies whether network connectivity is up.

    :returns: True if connected else False.
    """
    try:
        host = socket.gethostbyname("www.github.com")
        socket.create_connection((host, 80), 2)
        return True
    except (socket.error, socket.herror, socket.timeout):
        pass
    return False


class ArmadaTestCase(testtools.TestCase):

    def setUp(self):
        super(ArmadaTestCase, self).setUp()
        self.useFixture(fixtures.FakeLogger('armada'))
        default.register_opts(CONF)

    def override_config(self, name, override, group=None):
        CONF.set_override(name, override, group)
        self.addCleanup(CONF.clear_override, name, group)

    def assertEmpty(self, collection):
        if isinstance(collection, list):
            self.assertEqual(0, len(collection))
        elif isinstance(collection, dict):
            self.assertEqual(0, len(collection.keys()))

    def patch(self, target, autospec=True, **kwargs):
        """Returns a started `mock.patch` object for the supplied target.

        The caller may then call the returned patcher to create a mock object.

        The caller does not need to call stop() on the returned
        patcher object, as this method automatically adds a cleanup
        to the test class to stop the patcher.

        :param target: String module.class or module.object expression to patch
        :param **kwargs: Passed as-is to `mock.patch`. See mock documentation
                         for details.
        """
        p = mock.patch(target, autospec=autospec, **kwargs)
        m = p.start()
        self.addCleanup(p.stop)
        return m

    def patchobject(self, target, attribute, new=mock.DEFAULT, autospec=True):
        """Convenient wrapper around `mock.patch.object`

        Returns a started mock that will be automatically stopped after the
        test ran.
        """

        p = mock.patch.object(target, attribute, new, autospec=autospec)
        m = p.start()
        self.addCleanup(p.stop)
        return m
