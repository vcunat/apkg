"""
This is 'rpm' apkg packaging style for RPM-based distros such as
Fedora, CentOS, SUSE, RHEL.
"""
import glob


SUPPORTED_DISTROS = [
    "fedora",
    "centos",
    "rhel",
    "sles",
    "opensuse",
    "oracle",
    "pidora",
]


def is_valid_packaging_template(path):
    for spec in glob.iglob("%s/*.spec" % path):
        return True
    return False
