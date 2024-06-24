DEPENDENCY_MAPPING = {
    "ruff": {
        "repo": "https://github.com/charliermarsh/ruff-pre-commit",
        "rev": "v${rev}",
    },
    "black": {
        "repo": "https://github.com/psf/black-pre-commit-mirror",
        "rev": "${rev}",
    },
    "isort": {
        "repo": "https://github.com/pycqa/isort",
        "rev": "${rev}",
    },
    "mypy": {
        "repo": "https://github.com/pre-commit/mirrors-mypy",
        "rev": "v${rev}",
    },
}
