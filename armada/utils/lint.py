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
import yaml
from armada import const


SCHEMAS = {}

def _load_schemas():
    schema_dir = os.path.dirname(
        os.path.realpath(__file__))
    for schema_file in os.listdir(schema_dir):
        with open(os.path.join(schema_dir, schema_file)) as f:
            for schema in yaml.safe_load_all(f):
                name = schema['metadata']['name']
                assert name not in SCHEMAS
                SCHEMAS[name] = schema['data']

def check_schema(document):
    if not type(document) == dict:
        pass

    schema_name = document.get('schema', '')

    if schema_name in SCHEMAS:
        try:
            jsonschema.validate(document.get('data'), SCHEMAS[schema_name])
        except Exception as e:
            raise Exception(e)
    else:
        pass


def validate_armada_documents(documents):
    _load_schemas()
    for doc in documents:
        check_schema(doc)

    return

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
