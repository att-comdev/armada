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

import os

import pytest
import yaml

from armada.handlers.manifest import Manifest
from armada import errors as ex

basepath = os.path.join(os.path.dirname(__file__))
base_manifest = '{}/templates/simple.yaml'.format(basepath)

with open(base_manifest) as f:
    documents = list(yaml.safe_load_all(f.read()))


def test_manifest_get_documents():
    manifest = Manifest(documents)

    assert len(manifest.charts) == 2
    assert len(manifest.groups) == 1
    assert len(manifest.manifest) is not None
    temp_doc = documents
    temp_doc.append({'schema': 'dummy'})
    manifest = Manifest(temp_doc)


def test_manifest_find_documents():
    manifest = Manifest(documents)

    # Scenario 1: find charts
    doc_name = 'blog-1'
    chart = manifest.find_chart_document(doc_name)

    assert chart is not None
    assert chart.get('metadata').get('name') == doc_name

    with pytest.raises(ex.HandlerError):
        manifest.find_chart_document('chart')

    # Scenario 2: find charts
    doc_name = 'blog-group'

    group = manifest.find_chart_group_document(doc_name)

    assert group is not None
    assert group.get('metadata').get('name') == doc_name

    with pytest.raises(ex.HandlerError):
        manifest.find_chart_group_document('chart')
