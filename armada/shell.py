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

import sys

from cliff import app
from cliff import commandmanager as cm

import armada
from armada import log

class ArmadaApp(app.App):
    def __init__(self, **kwargs):
        super(ArmadaApp, self).__init__(
            description='Armada - Upgrade and deploy your charts',
            version=armada.__version__,
            command_manager=cm.CommandManager('armada'),
            **kwargs)

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(ArmadaApp, self).build_option_parser(
            description, version, argparse_kwargs)
        return parser

    def configure_logging(self):
        super(ArmadaApp, self).configure_logging()
        log.set_console_formatter()
        log.silence_iso8601()


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    return ArmadaApp().run(argv)
