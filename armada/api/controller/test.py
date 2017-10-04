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

import json

import falcon

from armada import api
from armada.common import policy
from armada import const
from armada.handlers.tiller import Tiller
from armada.handlers.manifest import Manifest
from armada.utils.release import release_prefix


class Test(api.BaseResource):
    '''
    Test helm releases via release name
    '''

    @policy.enforce('armada:test_release')
    def on_get(self, req, resp, release):
        try:
            self.logger.info('RUNNING: %s', release)
            opts = req.params
            tiller = Tiller(tiller_host=opts.get('tiller_host', None),
                            tiller_port=opts.get('tiller_port', None))

            msg = tiller.testing_release(
                release, output=opts.get('output', False))

            resp.body = json.dumps(msg)
            resp.status = falcon.HTTP_200
            resp.content_type = 'application/json'

        except Exception as e:
            err_message = 'Failed to test {}: {}'.format(release, e)
            self.error(req.context, err_message)
            self.return_error(
                resp, falcon.HTTP_500, message=err_message)


class Tests(api.BaseResource):
    '''
    Test helm releases via a manifest
    '''

#    @policy.enforce('armada:tests_manifest')
    def on_post(self, req, resp):
        try:
            opts = req.params
            tiller = Tiller(tiller_host=opts.get('tiller_host', None),
                            tiller_port=opts.get('tiller_port', None))

            documents = self.req_yaml(req)
            armada_obj = Manifest(documents).get_manifest()
            prefix = armada_obj.get(const.KEYWORD_ARMADA).get(
                const.KEYWORD_PREFIX)
            known_releases = [release[0] for release in tiller.list_charts()]

            message = {
                'tests': {
                    'passed': [],
                    'skipped': [],
                    'failed': []
                }
            }

            for group in armada_obj.get(const.KEYWORD_ARMADA).get(
                    const.KEYWORD_GROUPS):
                for ch in group.get(const.KEYWORD_CHARTS):
                    release_name = release_prefix(
                        prefix, ch.get('chart').get('chart_name'))

                    if release_name in known_releases:
                        self.logger.info('RUNNING: %s tests', release_name)
                        msg = tiller.testing_release(release_name)

                        if not msg:
                            continue

                        test_status = msg['Status']
                        if test_status[0] == 'Test Passed':
                            self.logger.info("PASSED: %s", test_status[1])
                            message['tests']['passed'].append(test_status[1])
                        else:
                            self.logger.info("FAILED: %s", test_status[1])
                            message['tests']['failed'].append(test_status[1])
                    else:
                        self.logger.info(
                            'Release %s not found - SKIPPING', release_name)
                        message['tests']['skipped'].append(release_name)

            import pdb
            pdb.set_trace()

            resp.body = json.dumps(message)
            resp.status = falcon.HTTP_200
            resp.content_type = 'application/json'

        except Exception as e:
            err_message = 'Failed to test manifest: {}'.format(e)
            self.error(req.context, err_message)
            self.return_error(
                resp, falcon.HTTP_500, message=err_message)
