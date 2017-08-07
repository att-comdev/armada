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
#

from armada.conf import default

import json
from falcon import HTTP_200

from oslo_config import cfg
from oslo_log import log as logging

# Required Oslo configuration setup
default.register_opts()

from armada.handlers.tiller import Tiller as tillerHandler

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
DOMAIN = "armada"

logging.setup(CONF, DOMAIN)

class Status(object):
    def on_get(self, req, resp):
        '''
        get tiller status
        '''

        try:
            message = "Tiller Server is {}"
            if tillerHandler().tiller_status():
                resp.data = json.dumps({'message': message.format('Active')})
                LOG.info('Tiller Server is Active.')
            else:
                resp.data = json.dumps({'message': message.format('Not'
                                                                  ' Present')})
                LOG.info('Tiller Server is Not Present.')

        except Exception as e:
            LOG.error('{} error occrred with message {} retrieving tiller \
                      information.'.format(type(e).__name__, e.message))

            resp.data = json.dumps({'message': 'A server error occured while'
                                    ' retrieving tiller information. Check'
                                    ' the Armada log for more information.'})

        finally:
            resp.content_type = 'application/json'
            resp.status = HTTP_200


class Release(object):
    def on_get(self, req, resp):
        '''
        get tiller releases
        '''

        try:
            # Get tiller releases
            handler = tillerHandler()

            releases = {}
            for release in handler.list_releases():
                releases[release.name] = release.namespace

            resp.data = json.dumps({'releases': releases})

        except Exception as e:
            LOG.error('{} error occrred with message {} retrieving release \
                      information.'.format(type(e).__name__, e.message))

            resp.data = json.dumps({'message': 'A server error occured while'
                                    ' retrieving release information. Check'
                                    ' the Armada log for more information.'})

        finally:
            resp.content_type = 'application/json'
            resp.status = HTTP_200
