# SPDX-License-Identifier: GPL-3.0-or-later

FROM debian:buster
MAINTAINER Jakub Ružička <jakub.ruzicka@nic.cz>
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN apt-get update -qqq
RUN apt-get upgrade -y -qqq

# packaging deps
RUN apt-get install -y -qqq dpkg-dev debhelper-compat dh-python python3-all python3-setuptools python3-build python3-pip python3-venv
# basic deps
RUN apt-get install -y -qqq python3-jinja2 python3-distro python3-docopt python3-blessings python3-requests python3-toml python3-cached-property
# non-python deps
RUN apt-get install -y -qqq git
# deps not available in distro
RUN pip3 install htmllistparse
# testing deps
RUN apt-get install -y -qqq tox python3-pytest python3-pytest-sugar python3-pytest-cov
# linting deps
RUN apt-get install -y -qqq python3-flake8 pylint3
# doc deps
RUN pip3 install mkdocs mkdocs-macros-plugin
