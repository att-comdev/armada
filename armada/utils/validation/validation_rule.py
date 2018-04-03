# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
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

from armada.utils.validation.validation_message import ValidationMessage


class ValidationRule():
    """ValidationRule base class for manifest and document validations."""
    def __init__(self, description, name):
        """Initialize the ValidationRule object.

        :param description: A user-friendly description of the validation rule.
        :param name: A code in the format ``ARM000`` for the UCP Integration
            API Convention ``ValidationMessage`` message.
        """
        self.description = description
        self.name = name
        self.error_counter = 0
        self.messages = []

    def report_message(self, msg, docs, diagnostic, error, level):
        message = "%s: %s" % (self.description, msg)
        vmsg = ValidationMessage(message=message,
                                 error=error,
                                 name=self.name,
                                 documents=docs,
                                 level=level,
                                 diagnostic=diagnostic)
        self.messages.append(vmsg.get_output())
        # TODO(MarshM) get_output() ??
        return vmsg

    def report_error(self, msg, docs, diagnostic):
        self.error_counter = self.error_counter + 1
        return self.report_message(msg, docs, diagnostic, True, 'Error')

    def report_info(self, msg, docs, diagnostic):
        return self.report_message(msg, docs, diagnostic, False, 'Info')

    def report_warning(self, msg, docs, diagnostic):
        return self.report_message(msg, docs, diagnostic, False, 'Warning')
