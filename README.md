# Sync with poetry

[![Tests](https://github.com/floatingpurr/sync_with_poetry/actions/workflows/tests.yml/badge.svg)](https://github.com/floatingpurr/sync_with_poetry/actions/workflows/tests.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/floatingpurr/sync_with_poetry/main.svg)](https://results.pre-commit.ci/latest/github/floatingpurr/sync_with_poetry/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A .pre-commit hook for keeping in sync `.pre-commit-config.yaml` repos `rev` with packages version locked into `poetry.lock`. Check out pre-commit.com for more about the main framework.

## What problem does this hook solve?

When it comes to Python dependency management, [Poetry](https://python-poetry.org/) is one of the modern solutions to handle project dependencies. [Sometimes](https://stackoverflow.com/q/70127649/4820341), you might want to install dev dependencies locally (e.g., `black`, `flake8`, `isort`, `mypy`, ...) to make your IDE (e.g., VS Code) play nicely with dev packages. This approach usually turns on a live feedback as you code (e.g., suggestions, linting, formatting, errors highlighting). Poetry pins dev packages in `poetry.lock`.

This hook updates the `rev` of each `repo` in `.pre-commit-config.yaml` with the corresponding package version stored in `poetry.lock`.

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

## Supported packages

Supported packages are listed in [`db.py`](sync_with_poetry/db.py). Entries specify how to map a package to the corresponding repo, following this pattern:

```python
{
    "<package_name_in_PyPy>": {
        "repo": "<repo_url_for_the_hook>",
        "rev": "<revision_template>",
    }
}
```