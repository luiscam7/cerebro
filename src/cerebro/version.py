import toml


def get_version():
    with open("pyproject.toml", "r") as file:
        pyproject = toml.load(file)
    return pyproject["tool"]["poetry"]["version"]


__version__ = get_version()
