from typing import Optional

import yaml

# A lock file
LOCK_CONTENT = (
    "[[package]]\n"
    'name = "mypy"\n'
    'version = "0.910"\n'
    'description = "Optional static typing for Python"\n'
    'category = "dev"\n'
    "optional = false\n"
    'python-versions = ">=3.5"\n'
    "[[package]]\n"
    'name = "flake8"\n'
    'version = "4.0.1"\n'
    'description = "the modular source code checker: pep8 pyflakes and co"\n'
    'category = "dev"\n'
    "optional = false\n"
    'python-versions = ">=3.6"\n'
    "[[package]]\n"
    'name = "black"\n'
    'version = "21.11b1"\n'
    'description = "The uncompromising code formatter."\n'
    'category = "main"\n'
    "optional = false\n"
    'python-versions = ">=3.6.2"\n'
    "[[package]]\n"
    'name = "pytest"\n'
    'version = "6.2.5"\n'
    'description = "pytest: simple powerful testing with Python"\n'
    'category = "dev"\n'
    "optional = false\n"
    'python-versions = ">=3.6"\n'
    "[[package]]\n"
    'name = "foobarbaz"\n'
    'version = "1.0.1"\n'
    'description = "a dummy package"\n'
    'category = "dev"\n'
    "optional = false\n"
    'python-versions = ">=3.6"\n'
)

# A .pre-commit-config.yaml file
CONFIG_CONTENT = (
    "repos:\n"
    "  # local hooks\n"
    "  - repo: local\n"
    "    hooks:\n"
    "      - id: sync\n"
    "        name: sync with poetry\n"
    "        entry: swp\n"
    "        language: system\n"
    "        files: poetry.lock\n"
    "  # mypy\n"
    "  - repo: https://github.com/pre-commit/mirrors-mypy\n"
    "    rev: v0.812\n"
    "    hooks:\n"
    "      - id: mypy\n"
    "  # comment\n"
    "  - repo: https://github.com/pycqa/flake8\n"
    "    rev: 3.9.0\n"
    "    hooks:\n"
    "      - id: flake8\n"
    "        args: [--max-line-length=88]\n"
    "  - repo: https://github.com/psf/black\n"
    "    rev: 20.8b1 # this is a rev\n"
    "    hooks:\n"
    "      - id: black\n"
    "    # another repo\n"
    "  - repo: https://github.com/pycqa/isort\n"
    "    rev: 5.10.1\n"
    "    hooks:\n"
    "      - id: isort\n"
    "        args: [--filter-files]\n"
    "  - repo: https://example.org/fakepackages/foobarbaz\n"
    "    rev: 1.0.0\n"
    "    hooks:\n"
    "      - id: foobarbaz\n"
)


CUSTOM_DEPENDENCY_MAPPING = {
    "foobarbaz": {
        "repo": "https://example.org/fakepackages/foobarbaz",
        "rev": "${rev}",
    },
}


def get_repo_version(filename: str, repo: str) -> Optional[str]:
    """Return the version (i.e., rev) of a repo

    Args:
        filename (str): .pre-commit-config.yaml
        repo (str): repo URL

    Returns:
        Optional[str]: the version of the repo
    """

    with open(filename, "r") as stream:
        pre_commit_data = yaml.safe_load(stream)

    pre_config_repo = next(
        (item for item in pre_commit_data["repos"] if item["repo"] == repo), None
    )

    if pre_config_repo:
        return pre_config_repo["rev"]

    return None
