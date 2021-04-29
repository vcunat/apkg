# SPDX-License-Identifier: GPL-3.0-or-later

FROM debian:buster
MAINTAINER Jakub Ružička <jakub.ruzicka@nic.cz>
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
RUN apt-get install -y -qqq dpkg-dev debhelper-compat dh-python git python3-all python3-setuptools python3-pip
# basic deps
RUN apt-get install -y -qqq python3-jinja2 python3-distro python3-docopt python3-blessings python3-requests python3-toml python3-cached-property
# deps not available in distro
RUN pip3 install build htmllistparse
# testing deps
RUN apt-get install -y -qqq tox python3-pytest python3-pytest-sugar
