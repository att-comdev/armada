FROM python:3.5

MAINTAINER Armada Team

ENV DEBIAN_FRONTEND noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY . /armada
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      netbase \
      curl \
      git && \
    useradd -u 1000 -g users -d /armada armada && \
    chown -R armada:users /armada && \
    mv /armada/etc/armada /etc/ && \
    cd /armada && \
    python3 setup.py install && \
    rm -rf \
      /root/.cache \
      /var/lib/apt/lists/*

EXPOSE 8000

USER armada
WORKDIR /armada

ENTRYPOINT ["./entrypoint.sh"]
CMD ["server"]
