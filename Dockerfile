# https://github.com/kubernetes/ingress/tree/master/images/ubuntu-slim
FROM gcr.io/google_containers/ubuntu-slim:0.13

ENV DEBIAN_FRONTEND=noninteractive \
    PROJECT=armada \
    LIBGIT_VERSION=0.25.0 \
    PATH=/var/lib/armada/bin:$PATH \
    PORT=8000

ARG WHEELS_URL=http://127.0.0.1:8000/wheels.tar.gz

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        build-essential \
        cmake \
        curl \
        git \
        libffi-dev \
        python-all-dev \
    && LIBGIT_TMP=$(mktemp -d) \
    && curl -sSL https://github.com/libgit2/libgit2/archive/v$LIBGIT_VERSION.tar.gz | tar zx  --strip-components 1 -C ${LIBGIT_TMP} \
    && cd ${LIBGIT_TMP} \
    && cmake . \
    && cmake --build . --target install \
    && ldconfig \
    && rm -rf ${LIBGIT_TMP} \
    && apt-get purge --auto-remove -y \
        ca-certificates \
        build-essential \
        cmake \
        curl \
        git \
        libffi-dev \
        python-all-dev \
    && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

ADD . /opt/armada

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        netbase \
        python \
        virtualenv \
    && virtualenv /var/lib/armada/ \
    && . /var/lib/armada/bin/activate \
    && pip install -U pip \
    && pip install -U setuptools wheel \
    && WHEELS_DIR=$(mktemp -d) \
    && curl -sSL ${WHEELS_URL} | tar zx --strip-components 2 -C ${WHEELS_DIR}/ \
    && cd /opt/armada \
    && git init \
    && pip install --no-cache-dir --no-index --no-compile --find-links ${WHEELS_DIR} /opt/armada \
    && rm -rf ${WHEELS_DIR} \
    && groupadd -g 42424 ${PROJECT} \
    && useradd -u 42424 -g ${PROJECT} -M -d /var/lib/${PROJECT} -s /usr/sbin/nologin -c "${PROJECT} user" ${PROJECT} \
    && mkdir -p /etc/${PROJECT} /var/log/${PROJECT} /var/lib/${PROJECT} /var/cache/${PROJECT} \
    && chown ${PROJECT}:${PROJECT} /etc/${PROJECT} /var/log/${PROJECT} /var/lib/${PROJECT} /var/cache/${PROJECT} \
    && apt-get purge -y --auto-remove \
        curl \
        git \
        virtualenv \
    && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache \
    && find /usr/ /var/ -type f -name "*.pyc" -delete

USER armada
ENTRYPOINT ["/opt/armada/entrypoint.sh"]
CMD ["server"]
