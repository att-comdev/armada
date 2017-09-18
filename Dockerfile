FROM ubuntu:16.04

MAINTAINER Armada Team

ENV DEBIAN_FRONTEND noninteractive

COPY . /armada

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
      netbase \
      python-all \
      python3-pip \
      python-setuptools && \
    apt-get install -y \
      build-essential \
      curl \
      git \
      python3-minimal \
      python3-setuptools \
      python3-dev && \
    useradd -u 1000 -g users -d /armada armada && \
    chown -R armada:users /armada && \
    \
    cd /armada && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    python3 setup.py install && \
    \
    apt-get purge --auto-remove -y \
      build-essential \
      cmake \
      python-all-dev \
      curl && \
    apt-get clean -y && \
    rm -rf \
      /root/.cache \
      /var/lib/apt/lists/*

EXPOSE 8000

USER armada
WORKDIR /armada

ENTRYPOINT ["./entrypoint.sh"]
CMD ["server"]
