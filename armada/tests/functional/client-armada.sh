#!/usr/bin/env bash

set -ex

make build

#for x in $(kubectl get nodes | grep Ready | awk "{print $1}"); do
#    echo $x
#    kubectl label nodes $x ucp-control-plane=enabled
#done

# armada apply examples/keystone-manifest.yaml

HELM_VERSION='2.7.0'

if [ $(which kubectl) != '' ]; then
    curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl && \
        chmod +x ./kubectl && \
        sudo mv ./kubectl /usr/local/bin/kubectl
fi

if [ $(which helm) != '' ]; then
    curl -Lo helm.tar.gz https://storage.googleapis.com/kubernetes-helm/helm-v${HELM_VERSION}-linux-amd64.tar.gz && \
        tar -zxvf helm.tar.gz && \
        sudo mv linux-amd64/helm /usr/local/bin/helm && \
        rm -rf linux-amd64 && rm helm.tar.gz
fi

if [ $(which openstack) != '' ]; then
	pip install python-openstackclient
fi

export KEYSTONE_IP=$(kubectl get pods --all-namespaces -o wide | grep keystone-api | awk '{print $7}')

if [ -z $KEYSTONE_IP ]; then
	echo 'No OSH Keystone API found in kubernetes cluster'

    exit 1
fi


export OS_AUTH_URL=http://${KEYSTONE_IP}/v3/
export OS_IDENTITY_API_VERSION=3
export OS_PASSWORD=armada  # (optional)
export OS_PROJECT_DOMAIN_NAME=ucp
export OS_PROJECT_NAME=service
export OS_USERNAME=armada
export OS_USER_DOMAIN_NAME=ucp
export TOKEN=$(openstack token issue | grep id | awk '{print $4}' | head -n 1)
export ARMADA_IP=$(kubectl get pods --all-namespaces -o wide | grep armada-api | awk '{print $7}')
export HOST=http://$ARMADA_IP:8000

if [ -z $ARMADA_IP ]; then
	echo "Could not find helm api in cluster using localhost"
	export HOST=http://localhost:8000
fi

if [ -z $TOKEN ]; then
	echo "Could not obtain the Armada Token"
    exit 1
fi

WORK_DIR=${HOME}/armada
COMMAND="armada --api --token ${TOKEN} --url ${HOST}"


echo "Armada Client Get Status"
$COMMAND  tiller --status

echo "Armada Client Get Releases"
$COMMAND tiller --releases

echo "Armada Client Validate Manifest"
$COMMAND validate ${WORK_DIR}/examples/simple.yaml
$COMMAND validate ${WORK_DIR}/examples/keystone-manifest.yaml

echo "Armada Client Deploy Manifest"

echo 'Deploy the Armada Keystone manifest'
$COMMAND apply ${WORK_DIR}/examples/keystone-manifest.yaml

echo 'Deploy the Armada Keystone manifest using pre and post actions'
$COMMAND apply ${WORK_DIR}/examples/keystone-manifest.yaml --set chart:keystone:values.replicas=5


echo "Armada Client Upgrade Manifest via Values"
cat ${WORK_DIR}/examples/simple-ovr-values.yaml
$COMMAND apply ${WORK_DIR}/examples/simple.yaml --values ${WORK_DIR}/examples/simple-ovr-values.yaml
kubectl get pods -n blog-blog

echo "Armada Client Upgrade Manifest via Set"
$COMMAND apply ${WORK_DIR}/examples/simple.yaml --set=chart_group:blog-group:description="I AM A NEW SET VALUE" --set=chart:blog-1:values.new.value=sw
$COMMAND apply ${WORK_DIR}/examples/simple.yaml --set=chart_group:blog-group:description="I AM A NEW SET VALUE" --set=chart:blog-1:values.new.value=ww

helm delete --purge armada-blog-1 armada-blog-2 armada-chart-example
