"""
The default group of operations that pygooglecloud has
"""
import pylogconf.core
from pytconf import register_endpoint, register_main, config_arg_parse_and_launch
import google.auth

from pygooglecloud.static import APP_NAME, DESCRIPTION, VERSION_STR


@register_endpoint(
    description="get the current project id",
    configs=[],
)
def get_project_id() -> None:
    """
    This will go to ~/.config/gcloud/configurtions/config_default unless
    GOOGLE_APPLICATION_CREDENTIALS environment variable points to something else
    if ~/.config/gcloud/configurtions/config_default is missing this will throw an exception.
    """
    _, project_id = google.auth.default()
    assert project_id is not None, "Could not find a project configured"
    print(project_id)


@register_main(
    main_description=DESCRIPTION,
    app_name=APP_NAME,
    version=VERSION_STR,
)
def main():
    pylogconf.core.setup()
    config_arg_parse_and_launch()


if __name__ == '__main__':
    main()
