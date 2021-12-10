# Contributing

PRs are always welcome! When contributing to this repository, please first
discuss the change you wish to make via issue, email, or any other method before
making a change.

# Set up your dev environment

This repo exploits [Poetry](https://python-poetry.org/) and
[pre-commit.com](https://pre-commit.com/). Upon forking this repo, run the
following commands:

```bash
$ poetry install        # install main and dev dependencies
$ pre-commit install    # install local pre-commit hooks
$                       # you are done!
```

In order to set up VS Code for this project, settings (i.e., [.vscode](.vscode))
are checked in the codebase. Just ignore such a folder if you do not need it.
