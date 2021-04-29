# SPDX-License-Identifier: GPL-3.0-or-later

FROM ubuntu:focal
MAINTAINER Jakub Ružička <jakub.ruzicka@nic.cz>
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN apt-get update -qqq
RUN apt-get upgrade -y -qqq

# install add-apt-repository
RUN apt-get install -y -qqq software-properties-common
# add Knot DNS repo (needed by Knot Resolver as build dep)
RUN add-apt-repository ppa:cz.nic-labs/knot-dns-latest
# refresh repos
RUN apt-get update -qqq

# packaging deps
RUN apt-get install -y -qqq apt-utils dpkg-dev debhelper-compat dh-python git python3-all python3-setuptools python3-pip
# basic deps
RUN apt-get install -y -qqq python3-jinja2 python3-distro python3-docopt python3-blessings python3-requests python3-toml python3-cached-property
# deps not available in distro
RUN pip3 install build htmllistparse
# testing deps
RUN apt-get install -y -qqq tox python3-pytest python3-pytest-sugar
