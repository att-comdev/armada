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

import jsonschema

from oslo_log import log as logging

from armada.utils.validation.validation_rule import ValidationRule

LOG = logging.getLogger(__name__)


class SchemaValidator(ValidationRule):
    def __init__(self, validation_schemas):
        super().__init__('JSON Schema Validation', 'ARMxxx')
        self.validation_schemas = validation_schemas

    def validate(self, document):
        """Validates a document by subjecting it to JSON schema validation.

        :param dict document: The document to validate.

        :returns: Value that indicates whether validation may continue,
            and populates ValidationRule error details.
        :rtype: bool.
        """

        if not isinstance(document, dict):
            # TODO(MarshM) this throws all the way up to invocation
            raise TypeError('The provided input "%s" must be a dictionary.'
                            % document)
            # error_msg = 'The provided input "%s" must be a dictionary' % \
            #     document
            # diagnostic = 'Check input type.'
            # vmsg = self.report_error(error_msg, None, diagnostic)
            # LOG.error('Cannot process document, not a dictionary')
            # LOG.debug('ValidationMessage:\n%s', vmsg.get_output_json())
            # # exit out, not recoverable
            # return False

        schema = document.get('schema', '<missing>')
        document_name = document.get('metadata', {}).get('name', '<missing>')
        docs = [dict(schema=schema, doc_name=document_name)]

        LOG.debug('Validating document [%s] name= %s', schema, document_name)

        if schema in self.validation_schemas:
            try:
                validator = jsonschema.Draft4Validator(
                    self.validation_schemas[schema])

                for error in validator.iter_errors(document.get('data')):
                    error_msg = "Invalid document [%s] %s: %s." % \
                        (schema, document_name, error.message)
                    diagnostic = 'Fix identified document.'
                    vmsg = self.report_error(error_msg, docs, diagnostic)
                    LOG.info(error_msg)
                    LOG.debug('ValidationMessage:\n%s', vmsg.get_output_json())

            except jsonschema.SchemaError as e:
                error_msg = ('The built-in Armada JSON schema %s is invalid. '
                             'Details: %s.' % (e.schema, e.message))
                diagnostic = 'Armada is misconfigured.'
                vmsg = self.report_error(error_msg, None, diagnostic)
                LOG.error('Armada Schema error. Cannot run validation.')
                LOG.error('ValidationMessage:\n%s', vmsg.get_output_json())
                # exit out, not recoverable
                return False

        else:
            error_msg = 'Unsupported document type: [%s] %s' % \
                (schema, document_name)
            diagnostic = ('Please ensure document is one of the following '
                          'schema types: %s' %
                          list(self.validation_schemas.keys()))
            vmsg = self.report_warning(error_msg, docs, diagnostic)
            LOG.info(error_msg)
            LOG.debug('ValidationMessage:\n%s', vmsg.get_output_json())
            # Validation API doesn't care about this type, don't send

        return True
