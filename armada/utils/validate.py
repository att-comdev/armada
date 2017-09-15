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

import jsonschema
import os
import pkg_resources
import requests
import yaml

from oslo_log import log as logging

from armada.const import KEYWORD_ARMADA, KEYWORD_PREFIX, KEYWORD_GROUPS, \
    KEYWORD_CHARTS, KEYWORD_RELEASE

LOG = logging.getLogger(__name__)
# Creates a mapping between ``metadata.name``: ``data`` where the
# ``metadata.name`` is the ``schema`` of a manifest and the ``data`` is the
# JSON schema to be used to validate the manifest in question.
SCHEMAS = {}


def _get_schema_dir():
    return pkg_resources.resource_filename('armada', 'schemas')


def _load_schemas():
    """Populates ``SCHEMAS`` with the schemas defined in package
    ``armada.schemas``.

    """
    schema_dir = _get_schema_dir()
    for schema_file in os.listdir(schema_dir):
        with open(os.path.join(schema_dir, schema_file)) as f:
            for schema in yaml.safe_load_all(f):
                name = schema['metadata']['name']
                if name in SCHEMAS:
                    raise RuntimeError(
                        'Duplicate schema specified for: %s.' % name)
                SCHEMAS[name] = schema['data']


def validate_armada_manifest(manifest):
    """Validates an Armada manifest file output by
    :class:`armada.handlers.manifest.Manifest`.

    :param dict manifest: The manifest to validate.

    :returns: A tuple of (bool, string) where the first value indicates whether
        the validation succeeded or failed and the second value is the error
        message if the validation failed.
    :rtype: tuple.

    """

    # TODO(fmontei): Switch this to use `jsonschema.validate` just like
    # `validate_armada_document`.
    if not isinstance(manifest.get(KEYWORD_ARMADA, None), dict):
        message = 'Could not find top-level {} keyword'.format(KEYWORD_ARMADA)
        return False, message

    armada_object = manifest.get('armada')

    if KEYWORD_PREFIX not in armada_object:
        message = 'Could not find {} keyword'.format(KEYWORD_PREFIX)
        return False, message

    groups = armada_object.get(KEYWORD_GROUPS)

    if not isinstance(groups, list):
        message = '{} entry is of wrong type: {} (expected: {})'.format(
            KEYWORD_GROUPS, type(groups), 'list')
        return False, message

    for group in groups:
        for chart in group.get(KEYWORD_CHARTS):
            chart_obj = chart.get('chart')
            if KEYWORD_RELEASE not in chart_obj:
                message = 'Could not find {} keyword in {}'.format(
                    KEYWORD_RELEASE, chart_obj.get('release'))
                return False, message

    return True, None


def validate_armada_document(document):
    """Validates a document ingested by Armada by subjecting it to JSON schema
    validation.

    :param dict dictionary: The document to validate.

    :returns: A tuple of (bool, string) where the first value indicates whether
        the validation succeeded or failed and the second value is the error
        message if the validation failed.
    :rtype: tuple.
    :raises TypeError: If ``document`` is of type ``dict``.

    """
    if not isinstance(document, dict):
        raise TypeError('The provided input "%s" must be a dictionary.'
                        % document)

    schema = document.get('schema', '<missing>')
    document_name = document.get('metadata', {}).get('name', None)

    if schema in SCHEMAS:
        try:
            jsonschema.validate(document.get('data'), SCHEMAS[schema])
            return True, None
        except jsonschema.SchemaError as e:
            error_message = ('The built-in Armada JSON schema %s is invalid. '
                             'Details: %s.' % (e.schema, e.message))
            LOG.error(error_message)
            return False, error_message
        except jsonschema.ValidationError as e:
            error_message = ('Invalid document [%s] %s: %s.' %
                             (schema, document_name, e.message))
            return False, error_message
    else:
        error_message = (
            'Document [%s] %s is not supported.' %
            (schema, document_name))
        LOG.error(error_message)
        return False, error_message


def validate_armada_documents(documents):
    """Validates multiple Armada manifests.

    :param documents: List of Armada maanifests to validate.
    :type documents: :func:`list[dict]`.

    :returns: A list of error messages that may have occurred while attempting
        to validate ``documents``.
    :rtype: list
    """
    error_messages = []

    for document in documents:
        is_valid, error = validate_armada_document(document)
        if not is_valid:
            error_messages.append(error)

    return error_messages


def validate_manifest_url(value):
    try:
        return (requests.get(value).status_code == 200)
    except:
        return False


def validate_manifest_filepath(value):
    return os.path.isfile(value)


# Fill the cache.
_load_schemas()
