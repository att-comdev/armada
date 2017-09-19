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
# import yaml

import falcon
from oslo_log import log as logging

from armada import api
from armada.common import policy
from armada import const
from armada.handlers.tiller import Tiller
from armada.handlers.manifest import Manifest
from armada.utils.release import release_prefix

LOG = logging.getLogger(__name__)


class Test(api.BaseResource):
    '''
    Test helm releases via release name
    '''

    @policy.enforce('armada:test_release')
    def on_get(self, req, resp, release):
        try:
            self.logger.info('RUNNING: %s', release)
            tiller = Tiller()
            tiller_resp = tiller.testing_release(release)
            msg = {
                'result': '',
                'message': ''
            }

            if tiller_resp:
                test_status = getattr(
                    tiller_resp.info.status, 'last_test_suite_run', 'FAILED')

                if test_status.result[0].status:
                    msg['result'] = 'PASSED: {}'.format(release)
                    msg['message'] = 'MESSAGE: Test Pass'
                    self.logger.info(msg)
                else:
                    msg['result'] = 'FAILED: {}'.format(release)
                    msg['message'] = 'MESSAGE: Test Fail'
                    self.logger.info(msg)
            else:
                msg['result'] = 'FAILED: {}'.format(release)
                msg['message'] = 'MESSAGE: No test found'

            resp.data = json.dumps(msg)
            resp.status = falcon.HTTP_200
            resp.content_type = 'application/json'

        except Exception as e:
            self.error(req.context, "Helm Test Failed")
            self.return_error(
                resp,
                falcon.HTTP_400,
                message="Helm Test Failed: {}".format(e))


class Tests(api.BaseResource):
    '''
    Test helm releases via a manifest
    '''

    @policy.enforce('armada:tests_manifest')
    def on_post(self, req, resp):
        try:
            tiller = Tiller()
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
                        resp = tiller.testing_release(release_name)

                        if not resp:
                            continue

                        test_status = getattr(
                            resp.info.status, 'last_test_suite_run',
                            'FAILED')
                        if test_status.results[0].status:
                            self.logger.info("PASSED: %s", release_name)
                            message['test']['passed'].append(release_name)
                        else:
                            self.logger.info("FAILED: %s", release_name)
                            message['test']['failed'].append(release_name)
                    else:
                        self.logger.info(
                            'Release %s not found - SKIPPING', release_name)
                        message['test']['skipped'].append(release_name)

            resp.status = falcon.HTTP_200

            resp.data = json.dumps(message)
            resp.content_type = 'application/json'

        except Exception:
            self.error(req.context, "Failed: Invalid Armada Manifest")
            self.return_error(
                resp,
                falcon.HTTP_400,
                message="Failed: Invalid Armada Manifest")
