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

class Override(object):
    def __init__(self, config, overrides):
        self.config = config
        self.overrides = overrides

    def get_manifest(self):
        '''
        Retrieves the manifest override values from the set CLI --set flag.
        '''

        new_value = self.overrides.split('=')[1]
        keywords = self.overrides.split('=')[0].split('.')
        override_type = keywords[0]

        if override_type == KEYWORD_CHART:
            self._override_chart(keywords, new_value)
        elif override_type == KEYWORD_CHARTS:
            self._override_chart_group(keywords, new_value)
        elif override_type == KEYWORD_PREFIX:
            self._override_prefix(keywords, new_value)

        return self.config

    def _get_charts(self):
        '''
        Gets the charts present in the manifest.
        '''

        charts = []
        for ch_group in self.config['armada']['chart_groups']:
            for ch in ch_group['chart_group']:
                charts.append(ch['chart'])

        return charts

    def _override_chart(self, keywords, new_value):
        '''
        Overrides chart values present in the manifest.
        '''
        charts = self._get_charts()
        chart_name = keywords[1]

        for ch in charts:
            '''
            Overrides charts present in the manifest.
            '''
            if ch['chart_name'] == chart_name:
                value = ch

                for attr in keywords[2:-1]:
                    value = value[attr]

                value[keywords[-1]] = new_value
