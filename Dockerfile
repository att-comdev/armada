#https://github.com/kubernetes/ingress-nginx/tree/master/images/ubuntu-slim
FROM gcr.io/google_containers/ubuntu-slim:0.14

MAINTAINER Armada Team

ENV DEBIAN_FRONTEND noninteractive

COPY . /opt/armada

RUN set -xe ;\
    apt-get update ;\
    apt-get upgrade -y ;\
    apt-get install -y --no-install-recommends \
      netbase \
      libpython3.5 \
      python3-pip \
      build-essential \
      curl \
      git \
      python3-setuptools \
      python3-dev ;\
    mkdir -p /var/lib/armada ;\
    mv -v /opt/armada/etc /var/lib/armada ;\
    useradd -u 1000 -g users -d /var/lib/armada armada ;\
    chown -R armada:users /var/lib/armada ;\
    cd /opt/armada ;\
    pip3 install --upgrade pip ;\
    pip3 install -r requirements.txt ;\
    python3 setup.py install ;\
    apt-get purge --auto-remove -y \
      build-essential \
      curl \
      python3-dev ;\
    apt-get clean -y ;\
    rm -rf \
      /root/.cache \
      /var/lib/apt/lists/*

EXPOSE 8000

USER armada
WORKDIR /var/lib/armada

ENTRYPOINT ["/opt/armada/entrypoint.sh"]
CMD ["server"]
