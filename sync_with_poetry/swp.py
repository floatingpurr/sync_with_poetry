import argparse
import json
import re
from string import Template
from typing import Dict, List, Optional, Sequence

import yaml
from tomlkit.items import AoT
from tomlkit.toml_file import TOMLFile

from sync_with_poetry.db import DEPENDENCY_MAPPING

YAML_FILE = ".pre-commit-config.yaml"
REV_LINE_RE = re.compile(r'^(\s+)rev:(\s*)([\'"]?)([^\s#]+)(.*)(\r?\n)$')


class PoetryItems(object):
    """A class to get and filter poetry.lock packages to sync in .pre-commit-config.yaml"""

    def __init__(
        self,
        poetry_list: AoT,
        skip: List[str] = [],
        db: Dict[str, Dict[str, str]] = DEPENDENCY_MAPPING,
    ) -> None:
        """Create a PoetryItems collection

        Args:
            poetry_list (list): a list of packages coming from poetry.lock
            skip (Optional[list], optional): A list of packages to skip. Such packages won't
                                             be synchronized in .pre-commit-config.yaml.
                                             Defaults to [].
            db (Dict[str, Dict[str, str]], optional): A package-repo mapping. Defaults to DEPENDENCY_MAPPING.
        """

        self._poetry_lock = {}
        for package in poetry_list:

            # skip
            if package["name"] in skip:
                continue

            dependency_mapping = db.get(package["name"], None)

            if dependency_mapping:
                name = package["name"]
                repo = dependency_mapping["repo"]
                rev = Template(dependency_mapping["rev"]).substitute(
                    rev=package["version"]
                )
                self._poetry_lock[repo] = {"name": name, "rev": rev}

    def get_by_repo(self, repo: str) -> Optional[Dict[str, str]]:
        """Get a PreCommitRepo given its url

        Args:
            repo (str): The repo url

        Returns:
            Optional[Dict[str, str]]: a dictionary representing a repo data (name and version)
                                      e.g., {'name': 'black', 'rev': '22.8.0'}
        """
        return self._poetry_lock.get(repo)


def sync_repos(
    filename: str,
    skip: List[str] = [],
    config: str = YAML_FILE,
    db: Dict[str, Dict[str, str]] = DEPENDENCY_MAPPING,
) -> int:

    retv = 0

    toml = TOMLFile(filename)
    content = toml.read()

    assert isinstance(content["package"], AoT)
    poetry_items = PoetryItems(content["package"], skip, db)

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

        if pre_commit_repo["rev"] == match[4].replace('"', "").replace("'", ""):
            continue

        new_rev_s = yaml.dump({"rev": pre_commit_repo["rev"]}, default_style=match[3])
        new_rev = new_rev_s.split(":", 1)[1].strip()
        lines[idx] = f"{match[1]}rev:{match[2]}{new_rev}{match[5]}{match[6]}"
        print(f"[{pre_commit_repo['name']}] -> rev: {pre_commit_repo['rev']}")
        retv |= 1

    with open(config, "w", newline="") as f:
        f.write("".join(lines))
    return retv


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    # parser.add_argument(
    #     "--all",
    #     action="store_true",
    #     help="Scan all dependencies in poetry.lock (main and dev)",
    # )
    # See how to pass a list here: https://github.com/pre-commit/pre-commit/issues/971
    parser.add_argument("--skip", nargs="*", default=[], help="Packages to skip")
    parser.add_argument(
        "--config",
        type=str,
        default=YAML_FILE,
        help="Path to the .pre-commit-config.yaml file",
    )
    parser.add_argument(
        "--db",
        type=str,
        help="Path to a custom package list (json)",
    )
    args = parser.parse_args(argv)
    if args.db is None:
        mapping = DEPENDENCY_MAPPING
    else:
        with open(args.db, "r") as f:
            mapping = json.load(f)
    retv = 0
    for filename in args.filenames:
        retv |= sync_repos(filename, args.skip, args.config, mapping)
    return retv


if __name__ == "__main__":
    raise SystemExit(main())
