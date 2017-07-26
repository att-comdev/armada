FROM ubuntu:16.04
MAINTAINER Armada Team

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

CMD ["server"]

ENV \
    LIBGIT_VERSION=0.25.0 \
    USER=armada

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        git \
        git-review \
        libffi-dev \
        libgit2-dev \
        libssl-dev \
        netbase \
        python-dev \
        python-pip \
        python-virtualenv \
    && mkdir -p /root/armada/tools

WORKDIR /root/armada

COPY ./tools/libgit2.sh /root/armada/tools
RUN /root/armada/tools/libgit2.sh

COPY requirements.txt /root/armada
RUN pip install --upgrade setuptools urllib3 \
    && pip install -r requirements.txt pygit2==$LIBGIT_VERSION

COPY . /root/armada

RUN pip install -e .
