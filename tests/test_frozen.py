import pytest
from py._path.local import LocalPath

from sync_with_poetry import swp

# test cases for frozen revisions
# all these packages have version 1.0.0 in poetry.lock
TEST_REVS = [
    "    rev: 1.0.0\n",
    "    rev: 1.0.0 # frozen\n",
    "    rev: 1.0.0 # frozen: 2.0.0\n",
    "    rev: 6fd1ced85fc139abd7f5ab4f3d78dab37592cd5e # frozen: 2.0.0\n",
    "    rev: 6fd1ced85fc139abd7f5ab4f3d78dab37592cd5e # frozen: 1.0.0\n",
    "    rev: 6fd1ced85fc139abd7f5ab4f3d78dab37592cd5e # frozen\n",
    "    rev: 6fd1ced85fc139abd7f5ab4f3d78dab37592cd5e # frozen: 1.0.0 fav version\n",
    "    rev: 6fd1ced85fc139abd7f5ab4f3d78dab37592cd5e # frozen: 2.0.0 fav version\n",
    "    rev: 6fd1ced85fc139abd7f5ab4f3d78dab37592cd5e # fav version\n",
    "    rev: 6fd1ced85fc139abd7f5ab4f3d78dab37592cd5e\n",
]


TEST_REVS_UNFROZEN = [
    "    rev: 1.0.0\n",
    "    rev: 1.0.0 # frozen\n",
    "    rev: 1.0.0 # frozen: 2.0.0\n",
    "    rev: 1.0.0\n",
    "    rev: 1.0.0\n",
    "    rev: 1.0.0 # frozen\n",
    "    rev: 1.0.0 # fav version\n",
    "    rev: 1.0.0 # fav version\n",
    "    rev: 1.0.0 # fav version\n",
    "    rev: 1.0.0\n",
]

TEST_REVS_FROZEN = [
    "    rev: 1.0.0\n",
    "    rev: 1.0.0 # frozen\n",
    "    rev: 1.0.0 # frozen: 2.0.0\n",
    "    rev: 1.0.0\n",
    "    rev: 6fd1ced85fc139abd7f5ab4f3d78dab37592cd5e # frozen: 1.0.0\n",
    "    rev: 1.0.0 # frozen\n",
    "    rev: 6fd1ced85fc139abd7f5ab4f3d78dab37592cd5e # frozen: 1.0.0 fav version\n",
    "    rev: 1.0.0 # fav version\n",
    "    rev: 1.0.0 # fav version\n",
    "    rev: 1.0.0\n",
]

assert len(TEST_REVS) == len(TEST_REVS_UNFROZEN) == len(TEST_REVS_FROZEN)


def config_content(rev_line: str) -> str:
    return "repos:\n" "  - repo: test\n" + rev_line + "    hooks:\n" "      - id: test\n"


LOCK_CONTENT = (
    "[[package]]\n"
    'name = "test"\n'
    'version = "1.0.0"\n'
    'description = "a dummy package"\n'
    "optional = false\n"
    'python-versions = ">=3.6"\n'
)


DEPENDENCY_MAPPING = {
    "test": {
        "repo": "test",
        "rev": "${rev}",
    }
}


def run_and_check(tmpdir: LocalPath, rev_line: str, expected: str, frozen: bool) -> None:
    lock_file = tmpdir.join("poetry.lock")
    lock_file.write(LOCK_CONTENT)
    config_file = tmpdir.join(".pre-commit-yaml")
    config = config_content(rev_line)
    config_file.write(config)

    retv = swp.sync_repos(
        lock_file.strpath,
        frozen=frozen,
        db=DEPENDENCY_MAPPING,
        config=config_file.strpath,
    )

    fixed_lines = open(config_file.strpath).readlines()
    fixed_rev_line = fixed_lines[2]

    assert fixed_rev_line == expected

    assert len(config.splitlines()) == len(fixed_lines)
    assert retv == int(expected != rev_line)


@pytest.mark.parametrize("rev_line,expected", zip(TEST_REVS, TEST_REVS_UNFROZEN))
def test_frozen_disabled(tmpdir: LocalPath, rev_line: str, expected: str) -> None:
    run_and_check(tmpdir, rev_line, expected, frozen=False)


@pytest.mark.parametrize("rev_line,expected", zip(TEST_REVS, TEST_REVS_FROZEN))
def test_frozen_enabled(tmpdir: LocalPath, rev_line: str, expected: str) -> None:
    run_and_check(tmpdir, rev_line, expected, frozen=True)
