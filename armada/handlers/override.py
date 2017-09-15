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

from armada import const
from armada.exceptions import override_exceptions
from armada.utils import validate


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
            with open(doc) as f:
                return list(yaml.safe_load_all(f.read()))
        except IOError:
            raise override_exceptions.InvalidOverrideFileException(doc)

    def update(self, d, u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                r = self.update(d.get(k, {}), v)
                d[k] = r
            elif isinstance(v, str) and isinstance(d.get(k), (list, tuple)):
                d[k] = [x.strip() for x in v.split(',')]
            else:
                d[k] = u[k]
        return d

    def find_document_type(self, alias):
        if alias == 'chart_group':
            return const.DOCUMENT_GROUP
        if alias == 'chart':
            return const.DOCUMENT_CHART
        if alias == 'manifest':
            return const.DOCUMENT_MANIFEST
        else:
            raise ValueError("Could not find {} document".format(alias))

    def find_manifest_document(self, doc_path):
        for doc in self.documents:
            if doc.get('schema') == self.find_document_type(
                doc_path[0]) and doc.get('metadata').get(
                    'name') == doc_path[1]:
                return doc

        raise override_exceptions.UnknownDocumentOverrideException(
            doc_path[0], doc_path[1])

    def array_to_dict(self, data_path, new_value):
        def convert(data):
            if isinstance(data, str):
                return str(data)
            elif isinstance(data, collections.Mapping):
                return dict(map(convert, data.items()))
            elif isinstance(data, collections.Iterable):
                return type(data)(map(convert, data))
            else:
                return data

        if not new_value:
            return

        if not data_path:
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
            if doc.get('schema') == const.DOCUMENT_CHART:
                self.update_chart_document(doc)
            if doc.get('schema') == const.DOCUMENT_GROUP:
                self.update_chart_group_document(doc)
            if doc.get('schema') == const.DOCUMENT_MANIFEST:
                self.update_armada_manifest(doc)

    def update_chart_document(self, ovr):
        for doc in self.documents:
            if doc.get('schema') == const.DOCUMENT_CHART and doc.get(
                    'metadata').get('name') == ovr.get('metadata').get('name'):
                self.update(doc.get('data'), ovr.get('data'))
                return

    def update_chart_group_document(self, ovr):
        for doc in self.documents:
            if doc.get('schema') == const.DOCUMENT_GROUP and doc.get(
                    'metadata').get('name') == ovr.get('metadata').get('name'):
                self.update(doc.get('data'), ovr.get('data'))
                return

    def update_armada_manifest(self, ovr):
        for doc in self.documents:
            if doc.get('schema') == const.DOCUMENT_MANIFEST and doc.get(
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
            validate.validate_armada_documents(self.documents)
        except Exception:
            raise override_exceptions.InvalidOverrideValueException(
                self.overrides)

        return self.documents
