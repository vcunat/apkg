# SPDX-License-Identifier: GPL-3.0-or-later

FROM ubuntu:bionic
MAINTAINER Jakub Ružička <jakub.ruzicka@nic.cz>
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/bin:${PATH}"

WORKDIR /root
CMD ["/bin/bash"]


RUN apt-get update -qqq
# upgrade system to latest
RUN apt-get upgrade -y -qqq

# install add-apt-repository
RUN apt-get install -y -qqq software-properties-common
# add Knot DNS repo (needed by Knot Resolver as build dep)
RUN add-apt-repository ppa:cz.nic-labs/knot-dns-latest
# refresh repos
RUN apt-get update -qqq

# packaging deps
RUN apt-get install -y -qqq apt-utils dpkg-dev debhelper dh-python git python3-all python3-pip
# basic deps
RUN apt-get install -y -qqq python3-jinja2 python3-docopt python3-blessings python3-toml python3-packaging
# deps not available/too old in distro
RUN pip3 install distro cached_property htmllistparse
# testing deps
RUN apt-get install -y -qqq tox python3-pytest python3-pytest-cov
