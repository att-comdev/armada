#!/bin/sh

set -ex

# Ubuntu 16.04 Install only

apt-get update
apt-get install -y \
    cmake \
    git \
    libffi-dev \
    libssh2-1 \
    libssh2-1-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libz-dev \
    make \
    pkg-config \
    python-dev \
    python-pip \
    wget

LIBGIT_VERSION=${LIBGIT_VERSION:-'0.25.0'}

wget https://github.com/libgit2/libgit2/archive/v${LIBGIT_VERSION}.tar.gz
tar xzf v${LIBGIT_VERSION}.tar.gz
cd libgit2-${LIBGIT_VERSION}/
cmake .
make
make install
ldconfig
