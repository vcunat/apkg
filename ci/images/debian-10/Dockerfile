# SPDX-License-Identifier: GPL-3.0-or-later

FROM debian:buster
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN apt-get update -qqq
RUN apt-get upgrade -y -qqq

# enable Knot DNS (required for Knot Resolver integration)
RUN apt-get -y -qqq install apt-transport-https lsb-release ca-certificates wget
RUN wget -O /etc/apt/trusted.gpg.d/knot-latest.gpg https://deb.knot-dns.cz/knot-latest/apt.gpg
RUN sh -c 'echo "deb https://deb.knot-dns.cz/knot-latest/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/knot-latest.list'
RUN apt-get update -qqq

# packaging deps
RUN apt-get install -y -qqq \
    apt-utils \
    build-essential \
    curl \
    debhelper \
    dh-python \
    dpkg-dev \
    git \
    python3-all \
    python3-pip \
    python3-setuptools
# testing deps
RUN apt-get install -y -qqq \
    python3-pytest \
    python3-pytest-sugar
# basic deps
RUN apt-get install -y -qqq \
    python3-blessings \
    python3-click \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml
# python deps not available\too old in distro
RUN pip3 install \
    build \
    htmllistparse
