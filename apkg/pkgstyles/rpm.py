"""
This is 'rpm' apkg package style for RPM-based distros such as
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
    "scientific",
]


def is_valid_package_template(path):
    for _ in glob.iglob("%s/*.spec" % path):
        return True
    return False


def get_package_name(path):
    return "TODO: rpm @ %s" % path
