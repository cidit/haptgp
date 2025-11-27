import tomllib
from tap import Tap
from typing import Literal


def get_pyproject(filepath="pyproject.toml"):
    with open(filepath, "rb") as f:
        pyproject = tomllib.load(f)
        return pyproject


class ArgumentParser(Tap):
    hello: bool = False
    env_file: str = ".env"
    calibrate: Literal["light"] | None = None

    def __init__(self, pyproject: dict[str, str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        name = pyproject["name"]
        version = pyproject["version"]
        description = pyproject["description"]
        self.description = f"""
            {name} v{version}
            {description}
        """
