""" python depedencies for this project """
from typing import List


console_scripts: List[str] = [
    "pygooglecloud=pygooglecloud.main:main",
]
dev_requires: List[str] = [
    "pypitools",
    "black",
]
config_requires: List[str] = [
    "pyclassifiers",
]
install_requires: List[str] = [
    "pylogconf",
    "pytconf",
    "google-auth",
]
build_requires: List[str] = [
    "pymakehelper",
    "pydmt",
]
test_requires: List[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "flake8",
    "mypy",
    "types-PyYAML",
]
requires = config_requires + install_requires + build_requires + test_requires
