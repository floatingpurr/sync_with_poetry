DEPENDENCY_MAPPING = {
    "autopep8": {
        "repo": "https://github.com/pre-commit/mirrors-autopep8",
        "rev": "v${rev}",
    },
    "black": {
        "repo": "https://github.com/psf/black",
        "rev": "${rev}",
    },
    "flake8": {
        "repo": "https://github.com/pycqa/flake8",
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
    "pyupgrade": {
        "repo": "https://github.com/asottile/pyupgrade",
        "rev": "v${rev}",
    },
    "flakeheaven": {
        "repo": "https://github.com/flakeheaven/flakeheaven",
        "rev": "${rev}",
    },
}
