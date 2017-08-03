FROM ubuntu:16.04

MAINTAINER Armada Team

ENV DEBIAN_FRONTEND noninteractive
ENV LIBGIT_VERSION 0.25.0

COPY . /armada

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
      netbase \
      python-all \
      python-pip \
      python-setuptools && \
    apt-get install -y \
      build-essential \
      cmake \
      curl \
      git \
      libffi-dev \
      python-all-dev && \
    useradd -u 1000 -g users -d /armada armada && \
    \
    curl -sSL https://github.com/libgit2/libgit2/archive/v$LIBGIT_VERSION.tar.gz \
      | tar zx -C /tmp && \
    cd /tmp/libgit2-$LIBGIT_VERSION && \
    cmake . && \
    cmake --build . --target install && \
    ldconfig && \
    \
    cd /armada && \
    pip install --upgrade pip && \
    pip install -r requirements.txt pygit2==$LIBGIT_VERSION && \
    pip install . && \
    \
    apt-get purge --auto-remove -y \
      build-essential \
      cmake \
      curl \
      git \
      libffi-dev \
      python-all-dev && \
    apt-get clean -y && \
    rm -rf \
      /root/.cache \
      /tmp/libgit2-$LIBGIT_VERSION \
      /var/lib/apt/lists/*

EXPOSE 8000

USER armada
WORKDIR /armada

ENTRYPOINT ["./entrypoint.sh"]
CMD ["server"]
