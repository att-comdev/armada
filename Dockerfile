FROM ubuntu:16.04

MAINTAINER Armada Team

ENV DEBIAN_FRONTEND noninteractive
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL=C

COPY . /armada

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
      netbase \
      python3-pip && \
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
      curl && \
    apt-get clean -y && \
    rm -rf \
      /root/.cache \
      /var/lib/apt/lists/*

RUN apt update && apt install curl -y

EXPOSE 8000

USER armada
WORKDIR /armada

ENTRYPOINT ["./entrypoint.sh"]
CMD ["server"]
