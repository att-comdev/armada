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

from ..const import KEYWORD_CHART, KEYWORD_CHARTS, KEYWORD_PREFIX
from ..exceptions import override_exceptions
from ..utils import lint

import copy
import yaml

class Override(object):
    def __init__(self, config, overrides=None, values=None):
        self.config = config
        self.overrides = overrides
        self.values = values

    def get_manifest(self):
        '''
        Overrides and retrieves a manifest using provided values method
        '''

        if self.values:
            # Override value dict
            if type(self.values) is not list:
                self._override_values_dict(values=self.values)

            # Values contains value files
            elif type(self.values) is dict:
                for doc in self.override_files:

                    # Retrieve nested dict of values and override
                    values = self._load_yaml_file(doc)
                    self._override_values_dict(values=values)

        # Override value list
        if self.overrides:

            # Parse keyword list
            for override in self.overrides:
                new_value = override.split('=')[1]
                keywords = override.split('=')[0].split('.')

                self._override_values_list(keywords, new_value)

        # Verify overrides do not invalidate config
        try:
            lint.validate_armada_object(self.config)
        except Exception:
            raise override_exceptions.InvalidOverrideValueException(
                self.overrides)

        return self.config

    def _get_charts(self):
        '''
        Retrieves a list of charts present in the config
        '''

        ch_groups = self._get_chart_groups()

        charts = []
        for ch_group in ch_groups:
            for ch in ch_group['chart_group']:
                charts.append(ch['chart'])

        return charts

    def _get_chart_groups(self):
        '''
        Retrieves a list of chart groups present in the config
        '''

        return [ch_gr for ch_gr in self.config['armada']['chart_groups']]

    def _override_chart(self, target, new_value):
        '''
        Overrides chart values present in the config
        '''

        charts = self._get_charts()
        chart_name = target[1]

        for ch in charts:
            if ch['chart_name'] == chart_name:
                value = ch

                for attr in target[2:-1]:
                    value = value[attr]

                value[target[-1]] = new_value

    def _override_chart_group(self, target, new_value):
        '''
        Overrides chart group values present in the config
        '''

        ch_groups = self._get_chart_groups()
        ch_grp_name = target[1]
        override_keyword = target[2]

        for ch_grp in ch_groups:
            if ch_grp['name'] == ch_grp_name:
                ch_grp[override_keyword] = new_value

    def _override_prefix(self, new_value):
        '''
        Overrides release prefix present in the config
        '''

        self.config['armada']['release_prefix'] = new_value

    def _override_values_list(self, target, new_value):
        '''
        Overrides a single value from a list of targets
        '''

        override_type = target[0]

        # Chart override
        if override_type == KEYWORD_CHART:
            self._override_chart(target, new_value)

        # Chart group override
        elif override_type == KEYWORD_CHARTS:
            self._override_chart_group(target, new_value)

        # Release prefix override
        elif override_type == KEYWORD_PREFIX:
            self._override_prefix(new_value)

        # Invalid override type
        else:
            raise override_exceptions.InvalidOverrideTypeException(
                override_type)

    def _load_yaml_file(self, doc):
        '''
        Retrieve yaml file as a dictionary.
        '''

        try:
            return list(yaml.safe_load_all(file(doc)))[0]
        except IOError:
            raise override_exceptions.InvalidOverrideFileException(doc)

    def _override_values_dict(self, values, target=None):
        '''
        Overrides manifest values using a nested dictionary of values
        '''

        if not target:
            target = []

        # End of value tree reached
        if type(values) is not dict:

            # Override target with new value
            new_value = values
            self._override_values_list(target, new_value)

        else:
            for key, value in values.iteritems():

                # Add key to list of targets
                override = copy.deepcopy(target)
                override.append(key)

                self._override_values_dict(values=value, target=override)
