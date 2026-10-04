# TOFIX

Findings from a code scan on 2026-10-04.

## Medium

- `src/pygooglecloud/main.py:65` - the array skipper only ends an array on a line that is exactly `)` (line 55) or a value that ends with `)`; a multi-line array whose closing paren follows the last element (`a=(x` / ` y)`) or a one-line array with a trailing comment (`a=(x y) # c`) leaves `in_array` set and silently swallows every later assignment (verified: `read_gcp_conf('a=(x\n y)\nb=2\n')` returns `{}`), so `gcp_configuration_name` can go missing. Track the closing paren on any line (ignoring trailing comments) and add tests for both shapes.
- `src/pygooglecloud/main.py:92` - relies on the private module `google.auth._cloud_sdk` (also line 164) for the gcloud config dir and ADC path; private APIs can change without notice in a `google-auth` release. Resolve the paths locally (`CLOUDSDK_CONFIG`, else `~/.config/gcloud` / `%APPDATA%\gcloud`) and drop the `google-auth` dependency, or at least cover the call with a test that fails loudly.

## Low

- `src/pygooglecloud/main.py:92` - the `# pylint: disable=protected-access` comments (also line 164) are leftovers: pylint is not run by `rsconstruct.toml` or listed in the dev group; delete them.
- `src/pygooglecloud/main.py:25` - `_die` always raises but is annotated `-> None`; annotate it `-> NoReturn` so type checkers know code after it is unreachable.
- `src/pygooglecloud/configs.py:4` - the module contains only a commented-out import and is still documented in `sphinx/pygooglecloud.rst:7-13`; delete it (and its sphinx section) or give it content.
- `doc/TODO.txt:1` - contains only "passed first run." / "passed first CI/CD." status notes, not TODO items; delete the file.
