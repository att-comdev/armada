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
CURRENT_DIR="$(pwd)"

function relative_run () {
  cd "${1}"
  bash -c "${2}"
  cd ${CURRENT_DIR}
}

#NOTE: Lint and package chart
make charts

#NOTE: Deploy command
: ${OSH_EXTRA_HELM_ARGS:=""}
helm upgrade --install armada ./charts/armada \
    --namespace=openstack \
    ${OSH_EXTRA_HELM_ARGS} \
    ${OSH_EXTRA_HELM_ARGS_ARMADA}

#NOTE: Wait for deploy
relative_run "${OSH_PATH}" "./tools/deployment/common/wait-for-pods.sh openstack"

#NOTE: Validate Deployment info
helm status armada
