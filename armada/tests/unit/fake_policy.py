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


policy_data = """
"admin_required": "role:admin"
"armada:create_endpoints": "rule:admin_required"
"armada:validate_manifest": "rule:admin_required"
"armada:test_release": "rule:admin_required"
"armada:test_manifest": "rule:admin_required"
"tiller:get_status": "rule:admin_required"
"tiller:get_release": "rule:admin_required"
"""
