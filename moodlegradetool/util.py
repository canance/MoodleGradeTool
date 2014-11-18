from contextlib import contextmanager

__author__ = 'phillip'



@contextmanager
def polyopen(f, *args, **kwargs):
    closeing = kwargs.pop("closing", False)
    if not (hasattr(f, 'read') or hasattr(f, "write")):
        f = open(f, *args, **kwargs)

    yield f

    if closeing:
        f.close()