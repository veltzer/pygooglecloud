"""
The default group of operations that pygooglecloud has
"""
import configparser
import json
import os
import sys

import pylogconf.core
from pytconf import register_endpoint, register_main, config_arg_parse_and_launch
import google.auth._cloud_sdk

from pygooglecloud.static import APP_NAME, DESCRIPTION, VERSION_STR

# Per-repo file (at the git root) naming the gcloud configuration to use.
GCP_CONF_FILE = ".gcp.conf"
GCP_CONF_KEY = "gcp_configuration_name"

_LOGIN_HINT = "Run: gcloud auth application-default login"


def _die(message: str) -> None:
    """Print a short, clear, single-line error to stderr and exit non-zero.

    No traceback: this command is meant to be called from shell startup
    (e.g. an auto-enter hook), so a wall of Python stack trace is just noise.
    """
    print(f"pygooglecloud: {message}", file=sys.stderr)
    raise SystemExit(1)


def _read_configuration_name() -> str:
    """Return the gcloud configuration name from ./.gcp.conf at the git root.

    The file is a flat key=value file, e.g.:
        gcp_configuration_name=machines
    """
    if not os.path.isfile(GCP_CONF_FILE):
        _die(f"no {GCP_CONF_FILE} found in the current directory (the git root).")
    # configparser needs a section header; .gcp.conf has none, so synthesize one.
    parser = configparser.ConfigParser()
    with open(GCP_CONF_FILE, encoding="utf-8") as stream:
        parser.read_string("[gcp]\n" + stream.read())
    name = parser["gcp"].get(GCP_CONF_KEY, "").strip()
    if not name:
        _die(f"{GCP_CONF_FILE} does not set {GCP_CONF_KEY}.")
    return name


def _read_project_from_configuration(name: str) -> str:
    """Return the [core] project from the gcloud configuration named `name`.

    Reads the on-disk gcloud configuration file directly (an INI file). This is
    a pure file read with no network call and no dependency on the gcloud CLI,
    which keeps invocation from a shell startup hook instant.
    """
    config_dir = google.auth._cloud_sdk.get_config_path()
    config_file = os.path.join(config_dir, "configurations", f"config_{name}")
    if not os.path.isfile(config_file):
        _die(f"gcloud configuration '{name}' not found at {config_file}.")
    parser = configparser.ConfigParser()
    parser.read(config_file, encoding="utf-8")
    project = parser.get("core", "project", fallback="").strip()
    if not project:
        _die(f"gcloud configuration '{name}' has no project set.")
    return project


@register_endpoint(
    description="get the current project id",
    configs=[],
)
def get_project_id() -> None:
    """
    Print the GCP project id for this repository.

    The project is resolved purely from local files (no network, no ADC):
    1. read ./.gcp.conf (at the git root) for the gcloud configuration name
    2. read that gcloud configuration's [core] project

    Failures are reported as short one-line messages, no traceback.
    """
    name = _read_configuration_name()
    print(_read_project_from_configuration(name))


def _is_valid_json_file(path: str) -> bool:
    """Return True if `path` is a file containing parseable JSON."""
    try:
        with open(path, encoding="utf-8") as stream:
            json.load(stream)
    except (OSError, ValueError):
        return False
    return True


@register_endpoint(
    description="check that Google credentials are present and well-formed",
    configs=[],
)
def check_credentials() -> None:
    """
    Verify that local Google credentials are present and well-formed.

    This is a pure local-file check with NO network call, so it is safe to run
    from a shell startup hook without slowing down directory changes. It does
    not (and cannot, without the network) detect a key that has been disabled
    or revoked server-side; it catches the common cases of a missing or
    corrupt credentials file.

    Two credential styles, with advice tailored to each:
    - service-account key: GOOGLE_APPLICATION_CREDENTIALS points at a JSON key
      file (as set per-repo from the .gcp.conf project). A missing or malformed
      file means the key needs to be (re)placed.
    - user login: no GOOGLE_APPLICATION_CREDENTIALS; the gcloud Application
      Default Credentials file is used, refreshed via `gcloud auth ... login`.

    On success this is silent (so it adds no noise to a shell startup hook);
    only failures are reported, on stderr, with a non-zero exit.
    """
    sa_key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if sa_key:
        if not os.path.isfile(sa_key):
            _die(f"service-account key not found at {sa_key}.")
        if not _is_valid_json_file(sa_key):
            _die(f"service-account key at {sa_key} is not valid JSON.")
        return

    adc_path = google.auth._cloud_sdk.get_application_default_credentials_path()
    if not os.path.isfile(adc_path):
        _die(f"no Google credentials found. {_LOGIN_HINT}")
    if not _is_valid_json_file(adc_path):
        _die(f"Google credentials at {adc_path} are malformed. {_LOGIN_HINT}")


@register_main(
    main_description=DESCRIPTION,
    app_name=APP_NAME,
    version=VERSION_STR,
)
def main():
    pylogconf.core.setup()
    config_arg_parse_and_launch()


if __name__ == "__main__":
    main()
