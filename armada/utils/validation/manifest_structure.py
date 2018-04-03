# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
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

from oslo_log import log as logging

from armada import const
from armada.utils.validation.validation_rule import ValidationRule

LOG = logging.getLogger(__name__)


class ManifestStructureValidator(ValidationRule):
    def __init__(self):
        super().__init__('Manifest Structure Check', 'ARMxxx')

    def validate(self, manifest, target_manifest=None):
        """ Validate that the manifest structure is correct, with exactly one
            "armada/Manifest/v1" and at least one of each
            "armada/ChartGroup/v1" and "armada/Chart/v1".

        Failing this check will halt further validations.

        :param Manifest manifest: The manifest to validate.
        :param str target_manifest: target_manifest, if set.
        """
        LOG.debug('Validating manifest structure.')

        # failing the validations below will halt further validations
        continue_running = True

        if len(manifest.manifests) > 1:
            error_msg = 'Multiple manifests are not supported.'
            documents = []
            for m in manifest.manifests:
                name = m.get('metadata', {}).get('name')
                documents.append(
                    dict(schema=const.DOCUMENT_MANIFEST, name=name))
            diagnostic = ('Ensure that the `target_manifest` option is set to '
                          'specify a single manifest.')

            self.report_error(error_msg, documents, diagnostic)
            continue_running = False

        if not all([manifest.charts, manifest.groups, manifest.manifests]):
            error_msg = ('Incorrect number of %s [%s], %s [%s], or %s [%s].' %
                         (const.DOCUMENT_CHART, len(manifest.charts),
                          const.DOCUMENT_GROUP, len(manifest.groups),
                          const.DOCUMENT_MANIFEST, len(manifest.manifests)))
            diagnostic = ('Manifest should be a list of documents that '
                          'includes at least one of each %s and %s, and '
                          'exactly one %s.' %
                          (const.DOCUMENT_CHART, const.DOCUMENT_GROUP,
                           const.DOCUMENT_MANIFEST))
            extra_diag = ''
            if len(manifest.manifests) == 0 and target_manifest:
                extra_diag = (' Did you specify the wrong target (%s)?' %
                              target_manifest)

            self.report_error(error_msg, None, diagnostic + extra_diag)
            continue_running = False

        return continue_running
