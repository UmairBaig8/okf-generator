"""Tests for okf.cli — command dispatch, version/help, and config commands."""

import sys

import pytest


@pytest.fixture
def isolated_config(monkeypatch, tmp_path):
    """Point okf.config.CONFIG_FILES at a temp file and restore afterwards."""
    import okf.config as config

    fake = tmp_path / "config.json"
    monkeypatch.setattr(config, "CONFIG_FILES", [fake])
    return fake


def _run_cli(args, capsys):
    """Run okf.cli.main() with the given argv, capturing output and exit."""
    from okf import cli
    old_argv = sys.argv
    sys.argv = ["okf"] + args
    try:
        try:
            cli.main()
            return 0
        except SystemExit as e:
            return e.code if e.code is not None else 0
    finally:
        sys.argv = old_argv


def test_cli_version(capsys):
    from okf import __version__
    code = _run_cli(["--version"], capsys)
    out = capsys.readouterr().out
    assert code == 0
    assert f"okf-generator v{__version__}" in out


def test_cli_version_short(capsys):
    code = _run_cli(["-v"], capsys)
    assert code == 0
    assert "okf-generator v" in capsys.readouterr().out


def test_cli_help_lists_commands(capsys):
    code = _run_cli(["--help"], capsys)
    out = capsys.readouterr().out
    assert code == 0
    for cmd in ("generate", "update", "lookup", "enrich", "serve", "dashboard", "config", "agent", "mcp"):
        assert cmd in out


def test_cli_unknown_command(capsys):
    code = _run_cli(["definitely-not-a-command"], capsys)
    assert code == 1
    err = capsys.readouterr().err
    assert "unknown" in err.lower() or "not" in err.lower()


def test_cli_config_read_shows_keys(capsys, isolated_config):
    """okf config (no args) prints known settings without crashing."""
    code = _run_cli(["config"], capsys)
    out = capsys.readouterr().out
    assert code == 0
    assert "llm" in out


def test_cli_config_write_and_coerce(capsys, isolated_config):
    """okf config serve.port=9090 writes an int, not a string."""
    assert not isolated_config.exists()

    _run_cli(["config", "serve.port=9090"], capsys)
    assert isolated_config.exists()

    from okf.config import _get, load
    cfg = load()
    port = _get(cfg, "serve.port", 0)
    assert isinstance(port, int)
    assert port == 9090


def test_cli_config_write_deep_key(capsys, isolated_config):
    """Dotted keys with >2 segments create nested sections."""
    _run_cli(["config", "enrich.deep.max_workers=4"], capsys)

    from okf.config import _get, load
    assert _get(load(), "enrich.deep.max_workers", 0) == 4
