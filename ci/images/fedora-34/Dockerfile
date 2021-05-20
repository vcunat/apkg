# SPDX-License-Identifier: GPL-3.0-or-later

FROM fedora:34

WORKDIR /root
CMD ["/bin/bash"]

# upgrade system to latest
RUN dnf upgrade -y

# packaging deps
RUN dnf install -y \
    git \
    rpm-build \
    python3-pip
# basic deps
RUN dnf install -y \
    python3-blessings \
    python3-cached-property \
    python3-distro \
    python3-docopt \
    python3-jinja2 \
    python3-packaging \
    python3-requests \
    python3-toml
# deps not available in distro
RUN pip3 install \
    htmllistparse
# testing deps
RUN dnf install -y \
    python3-pytest \
    python3-pytest-sugar
