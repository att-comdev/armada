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

from armada.const import DOCUMENT_CHART, DOCUMENT_GROUP, DOCUMENT_MANIFEST
from armada.const import KEYWORD_ARMADA, KEYWORD_PREFIX, KEYWORD_GROUPS, \
    KEYWORD_CHARTS, KEYWORD_RELEASE


def validate_armada_documents(documents):
    manifest = validate_manifest_document(documents)
    group = validate_chart_group_document(documents)
    chart = validate_chart_document(documents)

    return manifest and group and chart


def validate_armada_object(object):
    if not isinstance(object.get(KEYWORD_ARMADA, None), dict):
        raise Exception("Could not find {} keyword".format(KEYWORD_ARMADA))

    armada_object = object.get('armada')

    if armada_object.get(KEYWORD_PREFIX, None) is None:
        raise Exception("Could not find {} keyword".format(KEYWORD_PREFIX))

    if not isinstance(armada_object.get(KEYWORD_GROUPS), list):
        raise Exception('{} is of correct type: {} (expected: {} )'.format(
            KEYWORD_GROUPS, type(armada_object.get(KEYWORD_GROUPS)), list))

    for group in armada_object.get(KEYWORD_GROUPS):
        for chart in group.get(KEYWORD_CHARTS):
            chart_obj = chart.get('chart')
            if chart_obj.get(KEYWORD_RELEASE, None) is None:
                raise Exception('Could not find {} in {}'.format(
                    KEYWORD_RELEASE, chart_obj.get('release')))

    return True


def validate_manifest_document(documents):
    manifest_documents = []
    for document in documents:
        if document.get('schema') == DOCUMENT_MANIFEST:
            manifest_documents.append(document)
            manifest_data = document.get('data')
            if not manifest_data.get(KEYWORD_PREFIX, False):
                raise Exception(
                    'Missing {} keyword in manifest'.format(KEYWORD_PREFIX))
            if not isinstance(manifest_data.get('chart_groups'),
                              list) and not manifest_data.get(
                                  'chart_groups', False):
                raise Exception('Missing %s values. Expecting list type'.
                                format(KEYWORD_GROUPS))

        if len(manifest_documents) > 1:
            raise Exception(
                'Schema {} must be unique'.format(DOCUMENT_MANIFEST))

    return True


def validate_chart_group_document(documents):
    for document in documents:
        if document.get('schema') == DOCUMENT_GROUP:
            manifest_data = document.get('data')
            if not isinstance(manifest_data.get(KEYWORD_CHARTS),
                              list) and not manifest_data.get(
                                  'chart_group', False):
                raise Exception('Missing %s values. Expecting a list type'.
                                format(KEYWORD_CHARTS))

    return True


def validate_chart_document(documents):
    for document in documents:
        if document.get('schema') == DOCUMENT_CHART:
            manifest_data = document.get('data')
            if not manifest_data.get(KEYWORD_RELEASE, False):
                raise Exception(
                    'Missing %s values in %s. Expecting a string type'.format(
                        KEYWORD_RELEASE, document.get('metadata').get('name')))

    return True
