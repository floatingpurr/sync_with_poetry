import argparse
import re
from string import Template
from typing import List, Optional, Sequence

import yaml
from tomlkit.items import AoT
from tomlkit.toml_file import TOMLFile

from sync_with_poetry.db import DEPENDENCY_MAPPING

YAML_FILE = ".pre-commit-config.yaml"
REV_LINE_RE = re.compile(r'^(\s+)rev:(\s*)([\'"]?)([^\s#]+)(.*)(\r?\n)$')


class PreCommitRepo(object):
    """A simple class representing the version (i.e., rev) of a repo
    to sync in .pre-commit-config.yaml"""

    def __init__(self, name: str, repo: str, rev: str) -> None:
        self.name = name
        self.repo = repo
        self.rev = rev


class PoetryItems(object):
    """A class to get and filter poetry.lock packages to sync in .pre-commit-config.yaml"""

    def __init__(
        self,
        poetry_list: AoT,
        all: bool = False,
        skip: List[str] = [],
    ) -> None:
        """Create a PoetryItems collection

        Args:
            poetry_list (list): a list of packages coming from poetry.lock
            all (Optional[bool], optional): Set to True to consider all dependencies.
                                            Set to False for dev dependencies only.
                                            Defaults to False.
            skip (Optional[list], optional): A list of packages to skip. Such packages won't be synchronized in .pre-commit-config.yaml.
                                             Defaults to [].
        """

        self._poetry_list = []

        for package in poetry_list:

            # skip
            # if all == False and this package is not a dev dependency
            # or
            # if the package is in the skip list
            if ((not all) and package["category"] != "dev") or package["name"] in skip:
                continue

            dependency_mapping = DEPENDENCY_MAPPING.get(package["name"], None)

            if dependency_mapping:
                name = package["name"]
                repo = dependency_mapping["repo"]
                rev = Template(dependency_mapping["rev"]).substitute(
                    rev=package["version"]
                )
                self._poetry_list.append(PreCommitRepo(name, repo, rev))

    def get_by_repo(self, repo: str) -> Optional[PreCommitRepo]:
        """Get a PreCommitRepo gives its url

        Args:
            repo (str): The repo url

        Returns:
            Optional[PreCommitRepo]: a PreCommitRepo instance
        """
        return next(
            (package for package in self._poetry_list if package.repo == repo), None
        )


def sync_repos(
    filename: str, all: bool = False, skip: List[str] = [], config: str = YAML_FILE
) -> int:

    retv = 0

    toml = TOMLFile(filename)
    content = toml.read()

    assert isinstance(content["package"], AoT)
    poetry_items = PoetryItems(content["package"], all, skip)

    with open(config, "r") as stream:
        pre_commit_data = yaml.safe_load(stream)

    repo_pattern = []
    for repo in pre_commit_data["repos"]:
        if "rev" in repo:  # skip `repo: local`
            repo_pattern.append(poetry_items.get_by_repo(repo["repo"]))

    with open(config, newline="") as f:
        original = f.read()

    lines = original.splitlines(True)
    idxs = [i for i, line in enumerate(lines) if REV_LINE_RE.match(line)]

    for idx, pre_commit_repo in zip(idxs, repo_pattern):

        if pre_commit_repo is None:
            continue

        match = REV_LINE_RE.match(lines[idx])

        assert match is not None

        if pre_commit_repo.rev == match[4].replace('"', "").replace("'", ""):
            continue

        new_rev_s = yaml.dump({"rev": pre_commit_repo.rev}, default_style=match[3])
        new_rev = new_rev_s.split(":", 1)[1].strip()
        lines[idx] = f"{match[1]}rev:{match[2]}{new_rev}{match[5]}{match[6]}"
        print(
            f"[{pre_commit_repo.name}] {pre_commit_repo.repo}pyton -> rev: {pre_commit_repo.rev}"
        )
        retv |= 1

    with open(config, "w", newline="") as f:
        f.write("".join(lines))
    return retv


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan all dependencies in poetry.lock (main and dev)",
    )
    # See how to pass a list here: https://github.com/pre-commit/pre-commit/issues/971
    parser.add_argument("--skip", nargs="*", default=[], help="Packages to skip")
    parser.add_argument(
        "--config",
        type=str,
        default=YAML_FILE,
        help="Path to the .pre-commit-config.yaml file",
    )
    args = parser.parse_args(argv)
    retv = 0
    for filename in args.filenames:
        retv |= sync_repos(filename, args.all, args.skip, args.config)
    return retv


if __name__ == "__main__":
    raise SystemExit(main())
