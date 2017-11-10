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

import pytest

from armada.utils import release as rel


@pytest.mark.parametrize('prefix,name,expected', [
    ('armada', 'test', 'armada-test'),
    ('armada', 4, 'armada-4'),
    (4, 4, '4-4'),

])
def test_release_prefix(prefix, name, expected):
    assert rel.release_prefix(prefix, name) == expected


@pytest.mark.parametrize('label_dict,expected', [
    ({'a': 'b'}, 'a=b'),
    ({}, ''),
])
def test_label_selector(label_dict, expected):
    assert rel.label_selectors(label_dict) == expected
