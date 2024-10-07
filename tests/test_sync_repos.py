import pytest
from py._path.local import LocalPath

from sync_with_poetry import swp
from tests.helpers import CONFIG_CONTENT, CUSTOM_DEPENDENCY_MAPPING, LOCK_CONTENT, get_repo_version

LEN_CONFIG_CONTENT = CONFIG_CONTENT.count("\n")


# fmt: off
@pytest.mark.parametrize(
    "test_input,expected",
    [
        # sync all dependencies
        (
            {"skip": []},
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.910",     # bumped
                "https://github.com/pycqa/flake8": "4.0.1",                 # bumped
                "https://github.com/psf/black": "21.11b1",                  # bumped
                "https://github.com/pycqa/isort": "5.10.1",                 # not managed by Poetry
            },
        ),
        # sync dependencies, skipping `flake8` and black
        (
            {"skip": ["black", "flake8"]},
            # fmt: off
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.910",     # bumped
                "https://github.com/pycqa/flake8": "3.9.0",                 # not bumped skipped
                "https://github.com/psf/black": "20.8b1",                   # not bumped skipped
                "https://github.com/pycqa/isort": "5.10.1",                 # not managed by Poetry
            },
        ),
        # sync all dependencies from custom mapping
        (
            {"skip": [], "db": CUSTOM_DEPENDENCY_MAPPING},
            {
                "https://example.org/fakepackages/foobarbaz": "1.0.1",     # bumped (main)
            },

        ),
    ],
)
# fmt: on
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
        skip=["mypy", "flake8", "black"],
        config=config_file.strpath,
    )
    assert retv == 0
