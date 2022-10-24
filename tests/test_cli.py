#!/usr/bin/env python

"""Tests for `moralis_streams_client` CLI"""

import json
import shlex
from traceback import print_exception

import pytest
from click.testing import CliRunner

import moralis_streams_client
from moralis_streams_client import __version__
from moralis_streams_client.cli import cli


def test_version():
    """Test reading version and module name"""
    assert moralis_streams_client.__name__ == "moralis_streams_client"
    assert __version__
    assert isinstance(__version__, str)


@pytest.fixture
def run():
    runner = CliRunner()

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
        result = runner.invoke(cli, cmd, **kwargs)
        if result.exception:
            if expect_exception and isinstance(
                result.exception, expect_exception
            ):
                pass
            else:
                raise result.exception from result.exception
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
