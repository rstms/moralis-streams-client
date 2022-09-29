#!/usr/bin/env python

"""Tests for `moralis_streams_client` CLI"""

from traceback import print_exception

import pytest
from click.testing import CliRunner

import moralis_streams_client
from moralis_streams_client import __version__, cli


def test_version():
    """Test reading version and module name"""
    assert moralis_streams_client.__name__ == "moralis_streams_client"
    assert __version__
    assert isinstance(__version__, str)


@pytest.fixture
def run():
    runner = CliRunner()

    # env = os.environ.copy()
    # env['EXTRA_ENV_VAR'] = 'VALUE'

    def _run(cmd, **kwargs):
        expect_exit_code = kwargs.pop("expect_exit_code", 0)
        expect_exception = kwargs.pop("expect_exception", None)
        # kwargs["env"] = env
        result = runner.invoke(cli, cmd, **kwargs)
        if result.exception:
            if not isinstance(result.exception, expect_exception):
                print_exception(result.exception)
                breakpoint()
                pass
        else:
            assert result.exit_code == expect_exit_code, result.output
        return result

    return _run


def test_cli(run):
    """Test the CLI."""
    result = run([])
    assert "Usage:" in result.output


def test_help(run):
    result = run(["--help"])
    assert "Show this message and exit." in result.output
