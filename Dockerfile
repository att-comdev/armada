FROM ubuntu:16.04
MAINTAINER Armada Team

ARG VERSION
ARG REPO

ENV USER=armada \
    VERSION=${VERSION:-master} \
    REPO=${REPO:-https://github.com/att-comdev/armada.git}


RUN apt-get update -yqq && \
    apt-get install -yqq \
        build-essential \
        git \
        git-review \
        python-virtualenv \
        python-dev \
        python-pip \
        gcc \
        libssl-dev \
        libffi-dev \
        libgit2-dev

RUN git clone -b $VERSION $REPO ${HOME}/armada

WORKDIR /root/armada
RUN pip install -r requirements.txt \
    && sh tools/libgit2.sh \
    && pip install --upgrade urllib3 \
    && pip install pygit2==0.25.0 \
    && pip install -e .

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

CMD ["server"]
