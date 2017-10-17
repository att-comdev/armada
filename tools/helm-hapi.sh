#!/usr/bin/env bash

git clone https://github.com/kubernetes/helm ./helm -b $1

python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/chart/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/services/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/release/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. helm/_proto/hapi/version/*

find ./hapi/ -type d -exec touch {}/__init__.py \;
rm -rf ./helm
