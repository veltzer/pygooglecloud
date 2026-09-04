"""
.gcp.conf is bash-sourced by the gcloud_*.sh scripts, so the reader must
cope with everything bash accepts there: comments, blank lines, quoted
values, values that reference other variables, and arrays.
"""

from pygooglecloud.main import read_gcp_conf

SAMPLE = """
gcp_configuration_name=myworld

# Where and how the app is deployed.
gcp_project=id-veltzer-myworld
gcp_service="myworld"
gcp_region='us-central1'
gcp_service_account="${gcp_service}-app-sa@${gcp_project}.iam.gserviceaccount.com"

gcp_service_account_roles=(
\troles/cloudsql.client
\troles/secretmanager.secretAccessor
)
gcp_apis=(run.googleapis.com secretmanager.googleapis.com)
gcp_run_args=(
\t--allow-unauthenticated
\t--set-env-vars "A=1,B=2"
)
gcp_domain=myworld.stream
not an assignment
"""


def test_scalars_are_read() -> None:
    values = read_gcp_conf(SAMPLE)
    assert values["gcp_configuration_name"] == "myworld"
    assert values["gcp_project"] == "id-veltzer-myworld"
    assert values["gcp_domain"] == "myworld.stream"


def test_quotes_are_stripped_but_values_not_expanded() -> None:
    values = read_gcp_conf(SAMPLE)
    assert values["gcp_service"] == "myworld"
    assert values["gcp_region"] == "us-central1"
    assert values["gcp_service_account"] == "${gcp_service}-app-sa@${gcp_project}.iam.gserviceaccount.com"


def test_arrays_are_skipped_whole() -> None:
    values = read_gcp_conf(SAMPLE)
    for key in ("gcp_service_account_roles", "gcp_apis", "gcp_run_args"):
        assert key not in values
    # nothing inside an array leaks out as a key, and parsing resumes after it
    assert "roles/cloudsql.client" not in values
    assert list(values)[-1] == "gcp_domain"


def test_junk_is_ignored() -> None:
    assert not read_gcp_conf("")
    assert not read_gcp_conf("# only a comment\n\n")
    assert read_gcp_conf("gcp_configuration_name=x\n)\n") == {"gcp_configuration_name": "x"}
