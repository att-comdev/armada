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

from armada import const


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


def validate_armada_documents(documents):
    invalid_documents = []
    for document in documents:
        valid, err = validate_armada_document(document)
        if not valid:
            invalid_documents.append(err)

    if not invalid_documents:
        return True, invalid_documents

    return False, invalid_documents


def validate_armada_object(object):
    if not isinstance(object.get(const.KEYWORD_ARMADA, None), dict):
        raise Exception("Could not find {} keyword".format(
            const.KEYWORD_ARMADA))

    armada_object = object.get('armada')

    if not isinstance(armada_object.get(const.KEYWORD_PREFIX), str):
        raise Exception("Could not find {} keyword".format(
            const.KEYWORD_PREFIX))

    if not isinstance(armada_object.get(const.KEYWORD_GROUPS), list):
        raise Exception('{} is of correct type: {} (expected: {} )'.format(
            const.KEYWORD_GROUPS,
            type(armada_object.get(const.KEYWORD_GROUPS)), list))

    for group in armada_object.get(const.KEYWORD_GROUPS):
        for chart in group.get(const.KEYWORD_CHARTS):
            chart_obj = chart.get('chart')
            if not isinstance(chart_obj.get(const.KEYWORD_RELEASE), str):
                raise Exception('Could not find {} in {}'.format(
                    const.KEYWORD_RELEASE, chart_obj.get('name')))

    return True


# Fill the cache
_load_schemas()
