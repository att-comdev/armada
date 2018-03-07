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

from armada.const import KEYWORD_GROUPS, KEYWORD_CHARTS, KEYWORD_RELEASE
from armada.handlers.manifest import Manifest
from armada.exceptions.manifest_exceptions import ManifestException

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


def _validate_armada_manifest(manifest):
    """Validates an Armada manifest file output by
    :class:`armada.handlers.manifest.Manifest`.

    This will do business logic validation after the input
    files have be syntactically validated via jsonschema.

    :param dict manifest: The manifest to validate.

    :returns: A tuple of (bool, list[dict]) where the first value
        indicates whether the validation succeeded or failed and
        the second value is the validation details with a minimum
        keyset of (message(str), error(bool))
    :rtype: tuple.

    """
    details = []

    try:
        armada_object = manifest.get_manifest().get('armada')
    except ManifestException as me:
        details.append(dict(message=str(me), error=True))
        return False, details

    groups = armada_object.get(KEYWORD_GROUPS)

    if not isinstance(groups, list):
        message = '{} entry is of wrong type: {} (expected: {})'.format(
            KEYWORD_GROUPS, type(groups), 'list')
        details.append(dict(message=message, error=True))

    for group in groups:
        for chart in group.get(KEYWORD_CHARTS):
            chart_obj = chart.get('chart')
            if KEYWORD_RELEASE not in chart_obj:
                message = 'Could not find {} keyword in {}'.format(
                    KEYWORD_RELEASE, chart_obj.get('release'))
                details.append(dict(message=message, error=True))

    if len([x for x in details if x.get('error', False)]) > 0:
        return False, details

    return True, details


def validate_armada_manifests(documents):
    """Validate each Armada manifest found in the document set.

    :param documents: List of Armada documents to validate
    :type documents: :func: `list[dict]`.
    """
    messages = []
    all_valid = True

    for document in documents:
        if document.get('schema', '') == 'armada/Manifest/v1':
            target = document.get('metadata').get('name')
            manifest = Manifest(documents,
                                target_manifest=target)
            is_valid, details = _validate_armada_manifest(manifest)
            all_valid = all_valid and is_valid
            messages.extend(details)

    return all_valid, messages


def validate_armada_document(document):
    """Validates a document ingested by Armada by subjecting it to JSON schema
    validation.

    :param dict dictionary: The document to validate.

    :returns: A tuple of (bool, list[dict]) where the first value
        indicates whether the validation succeeded or failed and
        the second value is the validation details with a minimum
        keyset of (message(str), error(bool))
    :rtype: tuple.
    :raises TypeError: If ``document`` is not of type ``dict``.

    """
    if not isinstance(document, dict):
        raise TypeError('The provided input "%s" must be a dictionary.'
                        % document)

    schema = document.get('schema', '<missing>')
    document_name = document.get('metadata', {}).get('name', None)
    details = []

    if schema in SCHEMAS:
        try:
            validator = jsonschema.Draft4Validator(SCHEMAS[schema])
            for error in validator.iter_errors(document.get('data')):
                msg = "Invalid document [%s] %s: %s." % \
                    (schema, document_name, error.message)
                details.append(dict(message=msg,
                                    error=True,
                                    doc_schema=schema,
                                    doc_name=document_name))
        except jsonschema.SchemaError as e:
            error_message = ('The built-in Armada JSON schema %s is invalid. '
                             'Details: %s.' % (e.schema, e.message))
            LOG.error(error_message)
            details.append(dict(message=error_message, error=True))
    else:
        error_message = (
            'Document [%s] %s is not supported.' %
            (schema, document_name))
        LOG.info(error_message)
        details.append(dict(message=error_message, error=False))

    if len([x for x in details if x.get('error', False)]) > 0:
        return False, details

    return True, details


def validate_armada_documents(documents):
    """Validates multiple Armada documents.

    :param documents: List of Armada manifests to validate.
    :type documents: :func:`list[dict]`.

    :returns: A tuple of bool, list[dict] where the first value is whether
        the full set of documents is valid or not and the second is the
        detail messages from validation
    :rtype: tuple
    """
    messages = []
    # Track if all the documents in the set are valid
    all_valid = True

    for document in documents:
        is_valid, details = validate_armada_document(document)
        all_valid = all_valid and is_valid
        messages.extend(details)

    if all_valid:
        valid, details = validate_armada_manifests(documents)
        all_valid = all_valid and valid
        messages.extend(details)

    return all_valid, messages


def validate_manifest_url(value):
    try:
        return (requests.get(value).status_code == 200)
    except:
        return False


def validate_manifest_filepath(value):
    return os.path.isfile(value)


# Fill the cache.
_load_schemas()
