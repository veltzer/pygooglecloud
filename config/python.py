""" python deps for this project """

scripts: dict[str,str] = {
    "pygooglecloud": "pygooglecloud.main:main",
}

config_requires: list[str] = [
    "pyclassifiers",
]
install_requires: list[str] = [
    "pylogconf",
    "pytconf",
    "google-auth",
]
build_requires: list[str] = [
    "pydmt",
    "pymakehelper",
]
test_requires: list[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "mypy",
    # types
    "types-PyYAML",
]
requires = config_requires + install_requires + build_requires + test_requires
