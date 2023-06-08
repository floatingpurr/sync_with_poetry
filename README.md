# Sync with poetry

[![CI](https://github.com/floatingpurr/sync_with_poetry/actions/workflows/ci.yml/badge.svg)](https://github.com/floatingpurr/sync_with_poetry/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/floatingpurr/sync_with_poetry/branch/main/graph/badge.svg?token=RNDNWATE25)](https://codecov.io/gh/floatingpurr/sync_with_poetry)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/floatingpurr/sync_with_poetry/main.svg)](https://results.pre-commit.ci/latest/github/floatingpurr/sync_with_poetry/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A .pre-commit hook for keeping in sync the repos `rev` in
`.pre-commit-config.yaml` with the packages version locked into `poetry.lock`.
Check out [pre-commit.com](https://pre-commit.com/) for more about the main
framework.

> Do you rely on [PDM](https://github.com/pdm-project/pdm)? See this equivalent
> sync repo: [sync_with_pdm](https://github.com/floatingpurr/sync_with_pdm).

## What problem does this hook help us solve?

When it comes to Python dependency management,
[Poetry](https://python-poetry.org/) is one of the modern solutions to handle
project dependencies. [Sometimes](https://stackoverflow.com/q/70127649/4820341),
you might want to install dev dependencies locally (e.g., `black`, `flake8`,
`isort`, `mypy`, ...) to make your IDE (e.g., VS Code) play nicely with dev
packages. This approach usually turns on a live feedback as you code (e.g.,
suggestions, linting, formatting, errors highlighting). ~~Poetry pins dev
packages in `poetry.lock`~~ (not anymore, see
[#26](https://github.com/floatingpurr/sync_with_poetry/issues/26)).

This hook updates the `rev` of each `repo` in `.pre-commit-config.yaml` with the
corresponding package version stored in `poetry.lock`.

E.g., starting from the following files:

```toml
# poetry.lock
[[package]]
name = "black"
version = "21.12b0"
description = "The uncompromising code formatter."
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

```
  --skip [SKIP ...]  Packages to skip
  --config CONFIG    Path to a custom .pre-commit-config.yaml file
  --db PACKAGE_LIST  Path to a custom package list (json)
  --allow-frozen     Trust `frozen: xxx` comments for frozen revisions.
```

Usually this hook uses only dev packages to sync the hooks. Pass `--all`, if you
want to scan also the main project packages.

Pass `--skip <package_1> <package_2> ...` to disable the automatic
synchronization of the repos such packages correspond to.

Pass `--config <config_file>` to point to an alternative config file (it
defaults to `.pre-commit-config.yaml`).

Pass `--db <package_list_file>` to point to an alternative package list (json).
Such a file overrides the mapping in [`db.py`](sync_with_poetry/db.py).

Pass `--allow-frozen` if you want to use frozen revisions in your config.
Without this option _SWP_ will replace frozen revisions with the tag name taken
from `poetry.lock` even if the frozen revision specifies the same commit as the
tag. This options relies on `frozen: xxx` comments appended to the line of the
frozen revision where `xxx` will be the tag name corresponding to the commit
hash used. If the comment specifies the same revision as the lock file nothing
is changed. Otherwise the revision is replaced with the expected revision tag
and the `frozen: xxx` comment is removed.

## Supported packages

Supported packages out-of-the-box are listed in
[`db.py`](sync_with_poetry/db.py):

- autopep8
- bandit
- black
- commitizen
- flake8
- flakeheaven
- isort
- mypy
- pyupgrade

You can create your very own package list, passing a custom json file with the
arg `--db`. Such a file specifies how to map a package to the corresponding
repo, following this pattern:

```json
{
  "<package_name_in_PyPI>": {
    "repo": "<repo_url_for_the_package>",
    "rev": "<revision_template>"
  }
}
```

Sometimes the template of the version number of a package in PyPI differs from
the one used in the repo `rev`. For example, version `0.910` of `mypy` in PyPI
(no pun intended) maps to repo `rev: v0.910`. To make this hook aware of the
leading `v`, you need to specify `"v${rev}"` as a `"<revision_template>"`. Use
`"${rev}"` if both the package version and the repo `rev` follow the same
pattern.

Please, do not open PRs to extend [`db.py`](sync_with_poetry/db.py) anymore. Use
your personal package list instead.

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md).

## Credits

This hook is inspired by
[pre-commit autoupdate](https://pre-commit.com/index.html#pre-commit-autoupdate).
