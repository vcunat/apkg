# SPDX-License-Identifier: GPL-3.0-or-later

FROM ubuntu:xenial
MAINTAINER Jakub Ružička <jakub.ruzicka@nic.cz>
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN apt-get update -qqq
RUN apt-get upgrade -y -qqq

# basic deps
RUN apt-get install -y -qqq python3-pbr python3-jinja2 python3-docopt python3-blessings python3-toml
# testing deps
RUN apt-get install -y -qqq tox python3-pytest python3-pytest-cov
