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


import logging
import string
import sys

if sys.version_info < (2, 7):
    import functools

    @functools.wraps(logging.Formatter.format)
    def new_format(self, record, string=string,
                   old_format=logging.Formatter.format):
        if string.find is None:
            string.find = str.find
        return old_format(self, record)
    logging.Formatter.format = new_format


class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: '\033[00;32m',  # GREEN
        logging.INFO: '\033[00;36m',  # CYAN
        logging.WARN: '\033[01;33m',  # BOLD YELLOW
        logging.ERROR: '\033[01;31m',  # BOLD RED
        logging.CRITICAL: '\033[01;31m',  # BOLD RED
    }

    def format(self, record, Formatter=logging.Formatter):
        # Hack to get last log line instead of exception on 2.6
        res = Formatter.format(self, record)  # old-style class on 2.6
        return self.LEVEL_COLORS[record.levelno] + res + '\033[m'


def set_console_formatter(**formatter_kwargs):
    formatter_kwargs.setdefault(
        'fmt', '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    formatter_kwargs.setdefault('datefmt', '%m-%d %H:%M')
    root_logger = logging.getLogger('')
    for handler in root_logger.handlers:
        if handler.__class__ is logging.StreamHandler:  # Skip subclasses
            console_handler = handler
            # Skip if not a tty (default ssh, redirect, ...)
            isatty = getattr(handler.stream, 'isatty', None)
            if isatty is None or not isatty():
                continue
            break
    else:
        return  # Didn't find any suitable StreamHandlers there
    formatter = ColorFormatter(**formatter_kwargs)
    console_handler.setFormatter(formatter)


def silence_iso8601():
    iso8601_logger = logging.getLogger('iso8601')
    iso8601_logger.setLevel(logging.INFO)
