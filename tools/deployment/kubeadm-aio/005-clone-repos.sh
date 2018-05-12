#!/bin/bash

# Copyright 2018 The Openstack-Helm Authors.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

set -xe

: ${OSH_INFRA_PATH:="./deploy/openstack-helm-infra"}
: ${OSH_PATH:="./deploy/openstack-helm"}

if [ ! -d "${OSH_PATH}" ]; then
  mkdir -p $(dirname "${OSH_PATH}")
  git clone --depth 1 https://git.openstack.org/openstack/openstack-helm.git ${OSH_PATH}
fi

if [ ! -d "${OSH_INFRA_PATH}" ]; then
  mkdir -p $(dirname "${OSH_INFRA_PATH}")
  git clone --depth 1 https://git.openstack.org/openstack/openstack-helm-infra.git ${OSH_INFRA_PATH}
fi
