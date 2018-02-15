FROM python:3.5

MAINTAINER Armada Team

ENV DEBIAN_FRONTEND noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["server"]

RUN mkdir -p /armada && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        netbase \
        curl \
        git && \
    useradd -u 1000 -g users -d /armada armada && \
    rm -rf \
        /root/.cache \
        /var/lib/apt/lists/*

WORKDIR /armada

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY . /armada

RUN \
    mv /armada/etc/armada /etc/ && \
    cd /armada && \
    chown -R armada:users /armada && \
    python3 setup.py install

USER armada
