"""Print runtime and dependency versions for the portfolio PSO project."""

from __future__ import annotations

import platform
from importlib import metadata


DEPENDENCIES = ("numpy", "pandas", "fastapi")


def dependency_version(package_name: str) -> str:
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return "not installed"


def main() -> None:
    print(f"Python: {platform.python_version()}")
    for package_name in DEPENDENCIES:
        print(f"{package_name}: {dependency_version(package_name)}")


if __name__ == "__main__":
    main()
