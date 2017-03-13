#!/bin/sh

# Ubuntu 16.04 Install only

sudo apt install git cmake make -y
sudo apt-get install -y python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libssh2-1 libgit2-dev python-pip libgit2-24
sudo apt-get install -y pkg-config libssh2-1-dev libhttp-parser-dev libssl-dev libz-dev

LIBGIT_VERSION='0.25.0'

wget https://github.com/libgit2/libgit2/archive/v${LIBGIT_VERSION}.tar.gz
tar xzf v${LIBGIT_VERSION}.tar.gz
cd libgit2-${LIBGIT_VERSION}/
cmake .
make
sudo make install
sudo pip install pygit2==${LIBGIT_VERSION}
sudo ldconfig
