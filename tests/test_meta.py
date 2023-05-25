from sync_with_poetry import __version__


def test_version() -> None:
    """Test version"""
    assert __version__ == "1.0.0"
