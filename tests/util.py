import sys
from contextlib import contextmanager
from six import BytesIO


class TeeIO(BytesIO):
    """Like UNIX tee but for python streams.

    Inspired by CarbonCopy from Fabric.
    """

    def __init__(self, pipe=None, *args, **kwargs):
        """Construct a TeeIO object.

        :param pipe: a writable stream (default: sys.stdout).
        """
        self.pipe = pipe if pipe is not None else sys.stdout
        BytesIO.__init__(self, *args, **kwargs)

    def write(self, s):
        BytesIO.write(self, s)
        self.pipe.write(s)

    @contextmanager
    def as_manager(self):
        yield self
