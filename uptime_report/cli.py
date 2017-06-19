from __future__ import print_function, unicode_literals

import versioneer
from clize import run
from .config import write_config


def uptime():
    """Do the uptime reporting stuff."""
    pass


def version():
    """Get the version of this program."""
    return versioneer.get_version()


def main(**kwargs):
    """Run the CLI application."""
    run([uptime, write_config], alt=[version], **kwargs)

if __name__ == '__main__':
    main()
