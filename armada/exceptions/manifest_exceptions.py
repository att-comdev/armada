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

from armada.exceptions import base_exception as base


class ManifestException(base.ArmadaBaseException):
    """
    An exception occurred while attempting to build an Armada manifest. The
    exception will return with details as to why.

    **Troubleshoot:**
    *Coming Soon*
    """

    message = 'An error occurred while generating the manifest: %(details)s.'
