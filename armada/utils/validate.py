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

import os
import pkg_resources
import requests
import yaml

from oslo_log import log as logging

from armada.const import KEYWORD_GROUPS, KEYWORD_CHARTS, KEYWORD_RELEASE
from armada.const import DOCUMENT_MANIFEST
from armada.handlers.manifest import Manifest
from armada.exceptions.manifest_exceptions import ManifestException
from armada.utils.validation.manifest_structure import \
    ManifestStructureValidator
from armada.utils.validation.schema_validate import SchemaValidator
from armada.utils.validation.validation_message import ValidationMessage


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
        vmsg = ValidationMessage(message=str(me),
                                 error=True,
                                 name='ARM200',
                                 level='Error')
        LOG.error('ValidationMessage: %s', vmsg.get_output_json())
        details.append(vmsg.get_output())
        return False, details

    groups = armada_object.get(KEYWORD_GROUPS)

    if not isinstance(groups, list):
        message = '{} entry is of wrong type: {} (expected: {})'.format(
            KEYWORD_GROUPS, type(groups), 'list')
        vmsg = ValidationMessage(message=message,
                                 error=True,
                                 name='ARM101',
                                 level='Error')
        LOG.info('ValidationMessage: %s', vmsg.get_output_json())
        details.append(vmsg.get_output())

    for group in groups:
        for chart in group.get(KEYWORD_CHARTS):
            chart_obj = chart.get('chart')
            if KEYWORD_RELEASE not in chart_obj:
                message = 'Could not find {} keyword in {}'.format(
                    KEYWORD_RELEASE, chart_obj.get('release'))
                vmsg = ValidationMessage(message=message,
                                         error=True,
                                         name='ARM102',
                                         level='Error')
                LOG.info('ValidationMessage: %s', vmsg.get_output_json())
                details.append(vmsg.get_output())

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
        if document.get('schema', '') == DOCUMENT_MANIFEST:
            target = document.get('metadata', {}).get('name')
            manifest = Manifest(documents, target_manifest=target)

            # ManifestStructureValidator will ensure only 1 manifest
            validator = ManifestStructureValidator()
            continue_running = validator.validate(manifest, target)

            docs_valid = (validator.error_counter == 0)
            all_valid = all_valid and docs_valid
            messages.extend(validator.messages)

            if not continue_running:
                continue

            # Manifest passed previous check so there is only 1 manifest doc
            manifest.manifest = manifest.manifests[0] if manifest.manifests \
                else None

            is_valid, details = _validate_armada_manifest(manifest)
            all_valid = all_valid and is_valid
            messages.extend(details)

    return all_valid, messages


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
    continue_running = True

    for document in documents:
        # is_valid, details = validate_armada_document(document)
        # all_valid = all_valid and is_valid
        # messages.extend(details)

        validator = SchemaValidator(SCHEMAS)
        continue_running = validator.validate(document)

        docs_valid = (validator.error_counter == 0)
        all_valid = all_valid and docs_valid
        messages.extend(validator.messages)

        if not continue_running:
            continue

    if continue_running and all_valid:
        valid, details = validate_armada_manifests(documents)
        all_valid = all_valid and valid
        messages.extend(details)

    return all_valid, messages


def validate_manifest_url(value):
    try:
        return (requests.get(value).status_code == 200)
    except:
        return False


# TODO(MarshM) unused except in unit tests, is this useful?
def validate_manifest_filepath(value):
    return os.path.isfile(value)


# Fill the cache.
_load_schemas()
