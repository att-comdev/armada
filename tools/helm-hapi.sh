#!/bin/bash

git clone https://github.com/kubernetes/helm ./helm -b release-$1

python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/chart/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/services/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/release/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/version/*

rm -rf ./helm
