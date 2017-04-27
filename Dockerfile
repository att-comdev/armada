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

RUN useradd -ms /bin/bash $USER 
USER $USER 
WORKDIR /home/$USER

RUN git clone -b $VERSION https://github.com/att-comdev/armada.git

WORKDIR /home/$USER/armada
RUN virtualenv --no-site-packages /home/$USER/.armada && \
    . /home/$USER/.armada/bin/activate

RUN /home/$USER/.armada/bin/pip install -r /home/$USER/armada/requirements.txt
RUN /home/$USER/.armada/bin/python ./setup.py install

ENTRYPOINT ["/home/$USER/.armada/bin/armada"]
CMD ["-h"]
