"""
The default group of operations that pygooglecloud has
"""
import json
import os
import re
import sys

import pylogconf.core
from pytconf import config_arg_parse_and_launch, register_endpoint, register_main

from pygooglecloud.static import APP_NAME, DESCRIPTION, VERSION_STR

# Per-repo file (at the git root) naming the GCP project. The gcloud
# configuration for a project is named after its project ID.
GCP_CONF_FILE = ".gcp.conf"
GCP_CONF_KEY = "gcp_project"
# a bash assignment: name=value, with no spaces around the equals sign
_ASSIGNMENT = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")

_LOGIN_HINT = "Run: gcloud auth application-default login"


def _gcloud_config_dir() -> str:
    """Return the gcloud config directory, following gcloud's documented layout.

    google-auth only offers this through a private module, so the (stable,
    documented) rule is applied here: CLOUDSDK_CONFIG wins, otherwise
    %APPDATA%/gcloud on Windows and ~/.config/gcloud elsewhere.
    """
    override = os.environ.get("CLOUDSDK_CONFIG")
    if override:
        return override
    if os.name == "nt":
        return os.path.join(os.environ.get("APPDATA", ""), "gcloud")
    return os.path.join(os.path.expanduser("~"), ".config", "gcloud")


def _die(message: str) -> None:
    """Print a short, clear, single-line error to stderr and exit non-zero.

    No traceback: this command is meant to be called from shell startup
    (e.g. an auto-enter hook), so a wall of Python stack trace is just noise.
    """
    print(f"pygooglecloud: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_gcp_conf(text: str) -> dict[str, str]:
    """Return the scalar key=value assignments of a .gcp.conf.

    .gcp.conf is sourced by bash (the gcloud_*.sh scripts of utils-bash), so
    besides plain `key=value` lines it holds comments, blank lines and bash
    arrays such as:
        gcp_run_args=(
            --allow-unauthenticated
        )
    Only the scalar assignments matter here; arrays are skipped up to their
    closing parenthesis, and a one-line array `key=(...)` is skipped too.
    Values keep their surrounding quotes stripped but are not otherwise
    expanded, so a value that references another variable comes back as
    written.
    """
    values: dict[str, str] = {}
    in_array = False
    for raw in text.splitlines():
        line = raw.strip()
        if in_array:
            if line == ")":
                in_array = False
            continue
        if not line or line.startswith("#"):
            continue
        match = _ASSIGNMENT.match(line)
        if match is None:
            continue
        key, value = match.group(1), match.group(2).strip()
        if value.startswith("("):
            in_array = not value.endswith(")")
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values


def _read_project() -> str:
    """Return the GCP project ID from ./.gcp.conf at the git root."""
    if not os.path.isfile(GCP_CONF_FILE):
        _die(f"no {GCP_CONF_FILE} found in the current directory (the git root).")
    with open(GCP_CONF_FILE, encoding="utf-8") as stream:
        values = read_gcp_conf(stream.read())
    project = values.get(GCP_CONF_KEY, "")
    if not project:
        _die(f"{GCP_CONF_FILE} does not set {GCP_CONF_KEY}.")
    return project


@register_endpoint(
    description="get the current project id",
    configs=[],
)
def get_project_id() -> None:
    """
    Print the GCP project id for this repository.

    The project is read from gcp_project in ./.gcp.conf (at the git root), a
    pure local file read with no network and no ADC.

    Failures are reported as short one-line messages, no traceback.
    """
    print(_read_project())


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

    adc_path = os.path.join(_gcloud_config_dir(), "application_default_credentials.json")
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
