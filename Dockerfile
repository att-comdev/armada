FROM ubuntu:16.04
MAINTAINER bjozsa@att.com

ENV USER=armada \
    VERSION=master

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
        libgit2-dev

RUN useradd -ms /bin/bash armada
USER armada
WORKDIR /home/armada

RUN git clone -b $VERSION https://github.com/att-comdev/armada.git

WORKDIR /home/armada/armada
RUN virtualenv --no-site-packages /home/armada/.armada && \
    . /home/armada/.armada/bin/activate

RUN /home/armada/.armada/bin/pip install -r /home/armada/armada/requirements.txt
RUN /home/armada/.armada/bin/python ./setup.py install

ENTRYPOINT ["/home/armada/.armada/bin/armada"]
CMD ["-h"]
