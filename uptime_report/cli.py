from __future__ import print_function, unicode_literals

import versioneer
from clize import run
from .config import write_config
from .backends import list_backends


def uptime():
    """Do the uptime reporting stuff."""
    pass


def version():
    """Get the version of this program."""
    return versioneer.get_version()


def backends():
    """Print supported backends."""
    return "\n".join(list_backends())


def main(**kwargs):
    """Run the CLI application."""
    run([uptime, write_config], alt=[version, backends], **kwargs)

if __name__ == '__main__':
    main()
