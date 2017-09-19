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

import requests

from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class ArmadaSession(object):
    """
    A session to the Armada API maintaining credentials and API options

    :param string host: The armada server hostname or IP
    :param int port: (optional) The service port appended if specified
    :param string token: Auth token
    :param string marker: (optional) external context marker
    """

    def __init__(self, host, port=None, scheme='http', token=None,
                 marker=None):

        self._session = requests.Session()
        self._session.headers.update({
            'X-Auth-Token': token,
            'X-Context-Marker': marker
        })
        self.host = host
        self.scheme = scheme

        if port:
            self.port = port
            self.base_url = "{}://{}:{}/api/".format(
                self.scheme, self.host, self.port)
        else:
            self.base_url = "{}://{}/api/".format(
                self.scheme, self.host)

        self.token = token
        self.marker = marker
        self.logger = LOG

    # TODO Add keystone authentication to produce a token for this session
    def get(self, endpoint, query=None):
        """
        Send a GET request to armada.

        :param string endpoint: URL string following hostname and API prefix
        :param dict query: A dict of k, v pairs to add to the query string

        :return: A requests.Response object
        """
        api_url = '{}{}'.format(self.base_url, endpoint)
        resp = self._session.get(
            api_url, params=query, timeout=3600)

        return resp

    def post(self, endpoint, query=None, body=None, data=None):
        """
        Send a POST request to armada. If both body and data are specified,
        body will will be used.

        :param string endpoint: URL string following hostname and API prefix
        :param dict query: dict of k, v parameters to add to the query string
        :param string body: string to use as the request body.
        :param data: Something json.dumps(s) can serialize.
        :return: A requests.Response object
        """
        api_url = '{}{}'.format(self.base_url, endpoint)

        self.logger.debug("Sending POST with armada_client session")
        if body is not None:
            self.logger.debug("Sending POST with explicit body: \n%s" % body)
            resp = self._session.post(
                api_url, params=query, data=body, timeout=3600)
        else:
            self.logger.debug("Sending POST with JSON body: \n%s" % str(data))
            resp = self._session.post(
                api_url, params=query, json=data, timeout=3600)

        return resp
