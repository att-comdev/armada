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

import collections
import json
import yaml

from ..const import DOCUMENT_CHART, DOCUMENT_GROUP, DOCUMENT_MANIFEST
from ..exceptions import override_exceptions
from ..utils import lint


class Override(object):
    def __init__(self, documents, overrides=None, values=None):
        self.documents = documents
        self.overrides = overrides
        self.values = values

    def _load_yaml_file(self, doc):
        '''
        Retrieve yaml file as a dictionary.
        '''

        try:
            return list(yaml.safe_load_all(open(doc).read()))
        except IOError:
            raise override_exceptions.InvalidOverrideFileException(doc)

    def update(self, d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = self.update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    def find_document_type(self, alias):
        try:
            if alias == 'chart_group':
                return DOCUMENT_GROUP
            if alias == 'chart':
                return DOCUMENT_CHART
            if alias == 'manifest':
                return DOCUMENT_MANIFEST
            else:
                raise
        except Exception:
            msg = "Could not find {} document".format(alias)
            raise Exception(msg)

    def find_manifest_document(self, doc_path):
        try:
            for doc in self.documents:
                if doc.get('schema') == self.find_document_type(
                        doc_path[0]) and doc.get('metadata').get(
                            'name') == doc_path[1]:
                    return doc
            raise
        except Exception:
            raise override_exceptions.UnknownDocumentOverrideException(
                doc_path[0], doc_path[1])

    def array_to_dict(self, data_path, new_value):
        def convert(data):
            if isinstance(data, basestring):
                return str(data)
            elif isinstance(data, collections.Mapping):
                return dict(map(convert, data.iteritems()))
            elif isinstance(data, collections.Iterable):
                return type(data)(map(convert, data))
            else:
                return data

        if new_value is '':
            return

        if not len(data_path):
            return

        tree = {}

        t = tree
        for part in data_path:
            if part == data_path[-1]:
                t.setdefault(part, None)
                continue
            t = t.setdefault(part, {})

        string = json.dumps(tree).replace('null', '"{}"'.format(new_value))
        data_obj = convert(json.loads(string, encoding='utf-8'))

        return data_obj

    def override_manifest_value(self, doc_path, data_path, new_value):
        document = self.find_manifest_document(doc_path)
        new_data = self.array_to_dict(data_path, new_value)
        self.update(document.get('data'), new_data)

    def update_document(self, merging_values):

        for doc in merging_values:
            if doc.get('schema') == DOCUMENT_CHART:
                self.update_chart_document(doc)
            if doc.get('schema') == DOCUMENT_GROUP:
                self.update_chart_group_document(doc)
            if doc.get('schema') == DOCUMENT_MANIFEST:
                self.update_armada_manifest(doc)

    def update_chart_document(self, ovr):
        for doc in self.documents:
            if doc.get('schema') == DOCUMENT_CHART and doc.get('metadata').get(
                    'name') == ovr.get('metadata').get('name'):
                self.update(doc.get('data'), ovr.get('data'))
                return

    def update_chart_group_document(self, ovr):
        for doc in self.documents:
            if doc.get('schema') == DOCUMENT_GROUP and doc.get('metadata').get(
                    'name') == ovr.get('metadata').get('name'):
                self.update(doc.get('data'), ovr.get('data'))
                return

    def update_armada_manifest(self, ovr):
        for doc in self.documents:
            if doc.get('schema') == DOCUMENT_MANIFEST and doc.get(
                    'metadata').get('name') == ovr.get('metadata').get('name'):
                self.update(doc.get('data'), ovr.get('data'))
                return

    def update_manifests(self):

        if self.values:
            for value in self.values:
                merging_values = self._load_yaml_file(value)
                self.update_document(merging_values)

        if self.overrides:
            for override in self.overrides:
                new_value = override.split('=')[1]
                doc_path = override.split('=')[0].split(":")
                data_path = doc_path.pop().split('.')

                self.override_manifest_value(doc_path, data_path, new_value)

        try:
            lint.validate_armada_documents(self.documents)
        except Exception:
            raise override_exceptions.InvalidOverrideValueException(
                self.overrides)

        return self.documents
