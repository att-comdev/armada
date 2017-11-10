# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
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
"""Module for resolving design references."""

import urllib.parse
import re
import logging

import requests

from armada.exceptions.source_exceptions import InvalidPathException
from armada.utils.keystone import KeystoneUtils


class ReferenceResolver(object):
    """Class for handling different data references to resolve them data."""

    @classmethod
    def resolve_reference(cls, design_ref):
        """Resolve a reference to a design document.

        Locate a schema handler based on the URI scheme of the data reference
        and use that handler to get the data referenced.

        :param design_ref: A list of URI-formatted reference to a data entity
        :returns: A list of byte arrays
        """
        data = []
        if isinstance(design_ref, str):
            design_ref = [design_ref]

        for l in design_ref:
            try:
                design_uri = urllib.parse.urlparse(l)

                # when scheme is a empty string assume it is a local
                # file path
                if design_uri.scheme == '':
                    handler = cls.scheme_handlers.get('file')
                else:
                    handler = cls.scheme_handlers.get(design_uri.scheme, None)

                if handler is None:
                    raise InvalidPathException(
                        "Invalid reference scheme %s: no handler." %
                        design_uri.scheme)
                else:
                    # Have to do a little magic to call the classmethod
                    # as a pointer
                    data.append(handler.__get__(None, cls)(design_uri))
            except ValueError:
                raise InvalidPathException(
                    "Cannot resolve design reference %s: unable "
                    "to parse as valid URI."
                    % l)

        return data

    @classmethod
    def resolve_reference_http(cls, design_uri):
        """Retrieve design documents from http/https endpoints.

        Return a byte array of the response content. Support
        unsecured or basic auth

        :param design_uri: Tuple as returned by urllib.parse
                            for the design reference
        """
        if design_uri.username is not None and design_uri.password is not None:
            response = requests.get(
                design_uri.geturl(),
                auth=(design_uri.username, design_uri.password),
                timeout=30)
        else:
            response = requests.get(design_uri.geturl(), timeout=30)

        return response.content

    @classmethod
    def resolve_reference_file(cls, design_uri):
        """Retrieve design documents from local file endpoints.

        Return a byte array of the file contents

        :param design_uri: Tuple as returned by urllib.parse for the design
                           reference
        """
        if design_uri.path != '':
            with open(design_uri.path, 'rb') as f:
                doc = f.read()
            return doc

    @classmethod
    def resolve_reference_ucp(cls, design_uri):
        """Retrieve artifacts from a UCP service endpoint.

        Return a byte array of the response content. Assumes Keystone
        authentication required.

        :param design_uri: Tuple as returned by urllib.parse for the design
                           reference
        """
        ks_sess = KeystoneUtils.get_session()
        (new_scheme, foo) = re.subn('^[^+]+\+', '', design_uri.scheme)
        url = urllib.parse.urlunparse(
            (new_scheme, design_uri.netloc, design_uri.path, design_uri.params,
             design_uri.query, design_uri.fragment))
        logger = logging.getLogger(__name__)
        logger.debug("Calling Keystone session for url %s" % str(url))
        resp = ks_sess.get(url)
        if resp.status_code >= 400:
            raise InvalidPathException(
                "Received error code for reference %s: %s - %s" %
                (url, str(resp.status_code), resp.text))
        return resp.content

    scheme_handlers = {
        'http': resolve_reference_http,
        'file': resolve_reference_file,
        'https': resolve_reference_http,
        'deckhand+http': resolve_reference_ucp,
        'promenade+http': resolve_reference_ucp,
    }
