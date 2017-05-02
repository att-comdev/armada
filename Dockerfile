FROM ubuntu:16.04
MAINTAINER Armada Team

ENV USER=armada \
    VERSION=master \
    REPO=https://github.com/att-comdev/armada.git

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        git-review \
        python-virtualenv \
        python-dev \
        python-pip \
        gcc \
        libssl-dev \
        libffi-dev \
        libgit2-dev \

RUN git clone -b $VERSION $REPO ${HOME}/armada
WORKDIR /root/armada
RUN pip install -r requirements.txt \
    && sh scripts/libgit2.sh \
    && pip install --upgrade urllib3 \
    && pip install pygit2 \
    && python setup.py install

ENTRYPOINT ["armada"]

EXPOSE 8000

CMD gunicorn server:api -b :8000
