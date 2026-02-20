from importlib.metadata import version


__version__ = version("cerebro")


def get_version():
    return __version__
