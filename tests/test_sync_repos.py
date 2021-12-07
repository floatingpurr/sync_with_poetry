import pytest
from py._path.local import LocalPath

from sync_with_poetry import swp
from tests.helpers import CONFIG_CONTENT, LOCK_CONTENT, get_repo_version

LEN_CONFIG_CONTENT = CONFIG_CONTENT.count("\n")


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # sync only dev dependencies
        (
            {"all": False, "skip": []},
            # fmt: off
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.910",     # bumped (dev)
                "https://github.com/pycqa/flake8": "4.0.1",                 # not bumped (dev)
                "https://github.com/psf/black": "21.5b2",                   # bumped (main)
                "https://github.com/pycqa/isort": "5.10.1",                 # already in sync
            },
            # fmt: on
        ),
        # sync all dependencies (all = True)
        (
            {"all": True, "skip": []},
            # fmt: off
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.910",     # bumped (dev)
                "https://github.com/pycqa/flake8": "4.0.1",                 # bumped (dev)
                "https://github.com/psf/black": "21.11b1",                  # bumped (main)
                "https://github.com/pycqa/isort": "5.10.1",                 # already in sync
            },
            # fmt: on
        ),
        # sync only dev dependencies, skipping `flake8`
        (
            {"all": False, "skip": ["flake8"]},
            # fmt: off
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.910",     # bumped (dev)
                "https://github.com/pycqa/flake8": "3.9.0",                 # not bumped (dev), skipped
                "https://github.com/psf/black": "21.5b2",                   # not bumped (main)
                "https://github.com/pycqa/isort": "5.10.1",                 # already in sync
            },
            # fmt: on
        ),
        # sync all dependencies (all = True), skipping `black` and  `flake8`
        (
            {"all": True, "skip": []},
            # fmt: off
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.910",     # bumped (dev)
                "https://github.com/pycqa/flake8": "4.0.1",                 # bumped (dev)
                "https://github.com/psf/black": "21.11b1",                  # bumped (main)
                "https://github.com/pycqa/isort": "5.10.1",                 # already in sync
            },
            # fmt: on
        ),
        # sync dev dependencies, skipping untracked packages
        (
            {"all": False, "skip": ["black", "flake8"]},
            # fmt: off
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.910",     # bumped (dev)
                "https://github.com/pycqa/flake8": "3.9.0",                 # not bumped (dev), skipped
                "https://github.com/psf/black": "21.5b2",                   # not bumped (main), skipped
                "https://github.com/pycqa/isort": "5.10.1",                 # already in sync
            },
            # fmt: on
        ),
    ],
)
def test_sync_repos(tmpdir: LocalPath, test_input: dict, expected: dict) -> None:
    """Test repo synchronization against different inputs and configurations"""
    lock_file = tmpdir.join("poetry.lock")
    lock_file.write(LOCK_CONTENT)
    config_file = tmpdir.join(".pre-commit-yaml")
    config_file.write(CONFIG_CONTENT)

    retv = swp.sync_repos(lock_file.strpath, **test_input, config=config_file.strpath)

    for repo in expected:
        assert get_repo_version(config_file.strpath, repo) == expected[repo]

    assert LEN_CONFIG_CONTENT == len(open(config_file.strpath).readlines())
    assert retv == 1


def test_no_change(tmpdir: LocalPath) -> None:
    """Test a run without updates"""
    lock_file = tmpdir.join("poetry.lock")
    lock_file.write(LOCK_CONTENT)
    config_file = tmpdir.join(".pre-commit-yaml")
    config_file.write(CONFIG_CONTENT)
    retv = swp.sync_repos(
        lock_file.strpath,
        all=False,
        skip=["mypy", "flake8"],
        config=config_file.strpath,
    )
    assert retv == 0
