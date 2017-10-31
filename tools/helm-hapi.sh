#!/usr/bin/env bash

HELM_BRANCH=$1

if [ $HELM_BRANCH=='' ]; then
    HELM_BRANCH = 'release-2.6.0'
fi

git clone https://github.com/kubernetes/helm ./helm -b $HELM_BRANCH

python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/chart/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/services/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/release/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/version/*

find ./hapi/ -type d -exec touch {}/__init__.py \;
rm -rf ./helm
