import contextlib
import os
import sys
from collections.abc import Generator
from functools import partial

out = partial(print, file=sys.stderr)
err = partial(print, file=sys.stderr)


@contextlib.contextmanager
def suppress_stdout() -> Generator[None, None, None]:
    null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
    # Save the actual stdout (1) and stderr (2) file descriptors.
    save_fds = [os.dup(1), os.dup(2)]

    os.dup2(null_fds[0], 1)
    os.dup2(null_fds[1], 2)

    yield

    # Re-assign the real stdout/stderr back to (1) and (2)
    os.dup2(save_fds[0], 1)
    os.dup2(save_fds[1], 2)
    # Close the null files
    for fd in null_fds + save_fds:
        os.close(fd)
