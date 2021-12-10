# Sync with poetry

[![Tests](https://github.com/floatingpurr/sync_with_poetry/actions/workflows/tests.yml/badge.svg)](https://github.com/floatingpurr/sync_with_poetry/actions/workflows/tests.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/floatingpurr/sync_with_poetry/main.svg)](https://results.pre-commit.ci/latest/github/floatingpurr/sync_with_poetry/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A .pre-commit hook for keeping in sync the repos `rev` in
`.pre-commit-config.yaml` with the packages version locked into `poetry.lock`.
Check out [pre-commit.com](https://pre-commit.com/) for more about the main
framework.

## What problem does this hook solve?

When it comes to Python dependency management,
[Poetry](https://python-poetry.org/) is one of the modern solutions to handle
project dependencies. [Sometimes](https://stackoverflow.com/q/70127649/4820341),
you might want to install dev dependencies locally (e.g., `black`, `flake8`,
`isort`, `mypy`, ...) to make your IDE (e.g., VS Code) play nicely with dev
packages. This approach usually turns on a live feedback as you code (e.g.,
suggestions, linting, formatting, errors highlighting). Poetry pins dev packages
in `poetry.lock`.

This hook updates the `rev` of each `repo` in `.pre-commit-config.yaml` with the
corresponding package version stored in `poetry.lock`.

E.g., starting from the following files:

```toml
# poetry.lock
[[package]]
name = "black"
version = "21.12b0"
description = "The uncompromising code formatter."
category = "dev"
optional = false
python-versions = ">=3.6.2"
```

```yaml
# .pre-commit-config.yaml
repos:
  # black - formatting
  - repo: https://github.com/psf/black
    rev: 21.11b1
    hooks:
      - id: black
```

this hook will bump `black` in `.pre-commit-config.yaml` as follows:

```yaml
# .pre-commit-config.yaml
repos:
  # black - formatting
  - repo: https://github.com/psf/black
    rev: 21.12b0
    hooks:
      - id: black
```

## Usage

Excerpt from a `.pre-commit-config.yaml` using an example of this hook:

```yaml
- repo: https://github.com/floatingpurr/sync_with_poetry
  rev: "" # the revision or tag to clone at
  hooks:
    - id: sync_with_poetry
      args: [] # optional args
```

### Args

```bash
  --all              Scan all dependencies in poetry.lock (main and dev)
  --skip [SKIP ...]  Packages to skip
```

Usually this hook uses only dev packages to sync the hooks. Pass `--all`, if you
want to consider also the main project packages.

Pass `--skip <package_1> <package_2> ...` to disable the automatic
synchronization of the repos such packages correspond to.

## Supported packages

Supported packages are listed in [`db.py`](sync_with_poetry/db.py). Entries
specify how to map a package to the corresponding repo, following this pattern:

```python
{
    "<package_name_in_PyPI>": {
        "repo": "<repo_url_for_the_package>",
        "rev": "<revision_template>",
    }
}
```

Sometimes the template of the version number of a package in PyPI differs from
the one used in the repo `rev`. For example, version `0.910` of `mypy` in PyPI
(no pun intended) maps to repo `rev: v0.910`. To make this hook aware of this,
you need to specify `"v${rev}"` as a `"<revision_template>"`. Use `"${rev}"` if
package version and repo `rev` follow the same pattern. Sometimes the template
of the version number of a package in PyPI differs from the one used in the repo
`rev`. For example, version `0.910` of `mypy` in PyPI (no pun intended) maps to
repo `rev: v0.910`. To make this hook aware of the leading `v`, you need to
specify `"v${rev}"` as a `"<revision_template>"`. Use `"${rev}"` if both the
package version and the repo `rev` follow the same pattern.

PRs extending [`db.py`](sync_with_poetry/db.py) are welcome.

## Contributing

See CONTRIBUTING.md.

## Credits

This hook is inspired by
[pre-commit autoupdate](https://pre-commit.com/index.html#pre-commit-autoupdate).
