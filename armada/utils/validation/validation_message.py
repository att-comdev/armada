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

import json


class ValidationMessage(object):
    """ ValidationMessage per UCP convention:
    https://github.com/att-comdev/ucp-integration/blob/master/docs/source/api-conventions.rst#output-structure  # noqa

    Construction of ValidationMessage message:

    :param string message: Validation failure message.
    :param boolean error: True or False, if this is an error message.
    :param string name: Identifying name of the validation.
    :param string level: The severity of validation result, as "Error",
        "Warning", or "Info"
    :param array documents: An array of dicts containing the schema and name of
        the document(s) being validated.
    :param string diagnostic: Information about what lead to the message,
        or details for resolution.
    """

    def __init__(self,
                 message='Document validation error.',
                 error=True,
                 name='Armada error',
                 documents=None,
                 level='Error',
                 diagnostic=None):

        self.output = {
            'message': message,
            'error': error,
            'name': name,
            'documents': [],
            'level': level,
            'kind': 'ValidationMessage'
        }
        if documents:
            self.output['documents'].extend(documents)
        if diagnostic:
            self.output.update(diagnostic=diagnostic)

    def get_output(self):
        """ Return ValidationMessage message.

        :returns: The ValidationMessage for the Validation API response.
        :rtype: dict
        """
        return self.output

    def get_output_json(self):
        """ Return ValidationMessage message as JSON.

        :returns: The ValidationMessage formatted in JSON, for logging.
        :rtype: json
        """
        return json.dumps(self.output, indent=2)
