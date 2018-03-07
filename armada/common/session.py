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
    :param tuple timeout: (optional) a tuple of connect, read timeout values
        to use as the default for invocations using this session. A single
        value may also be supplied instead of a tuple to indicate only the
        read timeout to use
    """

    def __init__(self, host, port=None, scheme='http', token=None,
                 marker=None, timeout=None):

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

        self.default_timeout = ArmadaSession._calc_timeout_tuple((20, 3600),
                                                                 timeout)
        self.token = token
        self.marker = marker
        self.logger = LOG

    # TODO Add keystone authentication to produce a token for this session
    def get(self, endpoint, query=None, headers=None, timeout=None):
        """
        Send a GET request to armada.

        :param string endpoint: URL string following hostname and API prefix
        :param dict query: A dict of k, v pairs to add to the query string
        :param headers: Dictionary of HTTP headers to include in request
        :param timeout: A single or tuple value for connect, read timeout.
            A single value indicates the read timeout only
        :return: A requests.Response object
        """
        api_url = '{}{}'.format(self.base_url, endpoint)
        req_timeout = self._timeout(timeout)

        self.logger.debug("Sending armada_client session GET %s with "
                          "params=[%s], headers=[%s], timeout=[%s]",
                          api_url, query, headers, req_timeout)
        resp = self._session.get(
            api_url, params=query, headers=headers, timeout=req_timeout)

        return resp

    def post(self, endpoint, query=None, body=None, data=None, headers=None,
             timeout=None):
        """
        Send a POST request to armada. If both body and data are specified,
        body will will be used.

        :param string endpoint: URL string following hostname and API prefix
        :param dict query: dict of k, v parameters to add to the query string
        :param string body: string to use as the request body.
        :param data: Something json.dumps(s) can serialize.
        :param headers: Dictionary of HTTP headers to include in request
        :param timeout: A single or tuple value for connect, read timeout.
            A single value indicates the read timeout only
        :return: A requests.Response object
        """
        api_url = '{}{}'.format(self.base_url, endpoint)
        req_timeout = self._timeout(timeout)

        self.logger.debug("Sending armada_client session POST %s with "
                          "params=[%s], headers=[%s], timeout=[%s]",
                          api_url, query, headers, req_timeout)
        if body is not None:
            self.logger.debug("Sending POST with explicit body: \n%s" % body)
            resp = self._session.post(api_url,
                                      params=query,
                                      data=body,
                                      headers=headers,
                                      timeout=req_timeout)
        else:
            self.logger.debug("Sending POST with JSON body: \n%s" % str(data))
            resp = self._session.post(api_url,
                                      params=query,
                                      json=data,
                                      headers=headers,
                                      timeout=req_timeout)

        return resp

    def _timeout(self, timeout=None):
        """Calculate the default timeouts for this session

        :param timeout: A single or tuple value for connect, read timeout.
            A single value indicates the read timeout only
        :return: the tuple of the default timeouts used for this session
        """
        return ArmadaSession._calc_timeout_tuple(self.default_timeout, timeout)

    @classmethod
    def _calc_timeout_tuple(cls, def_timeout, timeout=None):
        """Calculate the default timeouts for this session

        :param def_timeout: The default timeout tuple to be used if no specific
            timeout value is supplied
        :param timeout: A single or tuple value for connect, read timeout.
            A single value indicates the read timeout only
        :return: the tuple of the timeouts calculated
        """
        connect_timeout, read_timeout = def_timeout

        try:
            if isinstance(timeout, tuple):
                if all(isinstance(v, int)
                        for v in timeout) and len(timeout) == 2:
                    connect_timeout, read_timeout = timeout
                else:
                    raise ValueError("Tuple non-integer or wrong length")
            elif isinstance(timeout, int):
                read_timeout = timeout
            elif timeout is not None:
                raise ValueError("Non integer timeout value")
        except ValueError:
            LOG.warn("Timeout value must be a tuple of integers or a single"
                     " integer. Proceeding with values of (%s, %s)",
                     connect_timeout,
                     read_timeout)
        return (connect_timeout, read_timeout)
