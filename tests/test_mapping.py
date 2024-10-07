import re

from sync_with_poetry.db import DEPENDENCY_MAPPING

# source: https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45
URL_REGEX = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def test_built_in_dependency_mapping() -> None:
    """Test the structure of the DEPENDENCY_MAPPING"""
    for item in DEPENDENCY_MAPPING:
        assert type(item) is str
        # chek url
        assert re.match(URL_REGEX, DEPENDENCY_MAPPING[item]["repo"])
        assert "${rev}" in DEPENDENCY_MAPPING[item]["rev"]
