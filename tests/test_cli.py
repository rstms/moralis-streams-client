#!/usr/bin/env python

"""Tests for `moralis_streams_client` CLI"""

import json
import shlex
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

    def _run(*args, **kwargs):
        if len(args) == 1 and isinstance(args[0], list):
            cmd = args[0]
        elif len(args) > 0:
            cmd = shlex.split(" ".join(list(args)))
        else:
            raise RuntimeError(f"args unexpected: {repr(args)}")
        expect_json = kwargs.pop("expect_json", False)
        expect_exit_code = kwargs.pop("expect_exit_code", 0)
        expect_exception = kwargs.pop("expect_exception", None)
        # kwargs["env"] = env
        result = runner.invoke(cli, cmd, **kwargs)
        if result.exception:
            if expect_exception is None or isinstance(
                result.exception, expect_exception
            ):
                print_exception(result.exception)
                breakpoint()
                pass
        else:
            assert result.exit_code == expect_exit_code, result.output
        if expect_json:
            result = json.loads(result.stdout)
        return result

    return _run


def test_cli_none(run):
    result = run([])
    assert "Usage:" in result.output


def test_cli_help(run):
    result = run(["--help"])
    assert "Show this message and exit." in result.output


def test_cli_get_stats(run):
    stats = run("get-stats", expect_json=True)
    print(json.dumps(stats, indent=2))
