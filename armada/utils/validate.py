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

import jsonschema
import os
import pkg_resources
import yaml

from oslo_log import log as logging

from armada import const

LOG = logging.getLogger(__name__)
SCHEMAS = {}


def _get_schema_dir():
    return pkg_resources.resource_filename('armada', 'schemas')


def _load_schemas():
    '''
    Fills the cache of known schemas
    '''
    schema_dir = _get_schema_dir()
    for schema_file in os.listdir(schema_dir):
        with open(os.path.join(schema_dir, schema_file)) as f:
            for schema in yaml.safe_load_all(f):
                name = schema['metadata']['name']
                if name in SCHEMAS:
                    raise RuntimeError(
                        'Duplicate schema specified for: %s' % name)

                SCHEMAS[name] = schema['data']


def validate_armada_document(document):
    if type(document) != dict:
        return

    schema_name = document.get('schema', '<missing>')
    document_name = document.get('metadata').get('name')

    if schema_name in SCHEMAS:
        try:
            jsonschema.validate(document.get('data'), SCHEMAS[schema_name])
            return True, None
        except jsonschema.ValidationError as e:
            err_message = "Invalid Document [{}] {}: {}".format(
                schema_name, document_name, e.message)
            return False, err_message
    else:
        LOG.warning(
            'Document [%s] is not supported: %s', schema_name, document_name)
        return True, None


def validate_armada_documents(documents):
    invalid_documents = []

    for document in documents:
        valid, err = validate_armada_document(document)
        if not valid:
            invalid_documents.append(err)

    if not invalid_documents:
        return True

    return invalid_documents


# Fill the cache
_load_schemas()
