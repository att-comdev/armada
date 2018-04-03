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
from copy import deepcopy

from oslo_log import log as logging

from armada import const
from armada.utils.validation.document_dependency import \
    DocumentDependencyValidator

LOG = logging.getLogger(__name__)


class Manifest(object):

    def __init__(self, documents, target_manifest=None):
        """Instantiates a Manifest object.

        An Armada Manifest expects that at least one of each of the following
        be included in ``documents``:

        * A document with schema "armada/Chart/v1"
        * A document with schema "armada/ChartGroup/v1"

        And only one document of the following is allowed:

        * A document with schema "armada/Manifest/v1"

        If multiple documents with schema "armada/Manifest/v1" are provided,
        specify ``target_manifest`` to select the target one.

        :param List[dict] documents: Documents out of which to build the
            Armada Manifest.
        :param str target_manifest: The target manifest to use when multiple
            documents with "armada/Manifest/v1" are contained in
            ``documents``. Default is None.
        :raises ManifestException: If the expected number of document types
            are not found or if the document types are missing required
            properties.
        """
        self.documents = deepcopy(documents)
        self.target_manifest = target_manifest
        # self.charts, self.groups, self.manifests =
        self._classify_documents()

    # TODO(MarshM) fix docstring
    def _classify_documents(self):
        """Establishes the chart documents, chart group documents,
        and Armada manifest(s)

        If multiple documents with schema "armada/Manifest/v1" are provided,
        specify ``target_manifest`` to select the target one.

        :param str target_manifest: The target manifest to use when multiple
            documents with "armada/Manifest/v1" are contained in
            ``documents``. Default is None.
        :returns: Tuple of chart documents, chart groups, and manifests
            found in ``self.documents``
        :rtype: tuple
        """
        self.charts = []
        self.groups = []
        self.manifests = []
        for document in self.documents:
            doc_schema = document.get('schema', '<missing>')
            if doc_schema == const.DOCUMENT_CHART:
                self.charts.append(document)
            elif doc_schema == const.DOCUMENT_GROUP:
                self.groups.append(document)
            elif doc_schema == const.DOCUMENT_MANIFEST:
                manifest_name = document.get('metadata', {}).get('name')
                if self.target_manifest:
                    if manifest_name == self.target_manifest:
                        self.manifests.append(document)
                else:
                    self.manifests.append(document)
            else:
                LOG.warn('unknown document type: %s', doc_schema)
        # return charts, groups, manifests

    def get_manifest(self):
        """Builds all of the documents including the dependencies of the
        chart documents, the charts in the chart_groups, and the
        Armada manifest

        :returns: The Armada manifest.
        :rtype: dict
        """

        validator = DocumentDependencyValidator()
        manifest_with_deps = validator.validate(self)

        # TODO(MarshM) Handle errors?
        if validator.error_counter > 0:
            LOG.info('Found [%s] document validation errors: %s',
                     validator.error_counter, validator.messages)

        return {
            'armada': manifest_with_deps.get('data')
        }
