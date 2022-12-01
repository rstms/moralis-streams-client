# cli tests

import logging
import os
import shlex
import subprocess

import pytest

from moralis_streams_client.webhook import Webhook

info = logging.info


@pytest.fixture
def run():
    def _run(cmd, check=True, expect_error=False):
        if isinstance(cmd, list):
            pass
        else:
            cmd = shlex.split(cmd)
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if check:
            if expect_error:
                assert proc.returncode != 0, proc
            else:
                assert proc.returncode == 0, proc
        return proc

    return _run


def as_lines(string):
    return string.strip().split("\n")


def test_cli_no_args(run):
    result = run("msc")
    assert result.stdout
    info(result.stdout)
    assert result.stdout.startswith("Usage:")


def test_cli_help(run):
    result = run("msc", "--help")
    assert result.stdout
    info(result.stdout)


async def test_cli_start_stop(run):
    run("webhook -p 8082 ps", expect_error=True)
    run("webhook -p 8082 -d -l DEBUG -T start")
    run("webhook -p 8082 ps")
    ret = run("webhook -p 8082 hello")
    assert "Hello, Webhook!" in ret.stdout
    await Webhook(port=8082).stop()
    # run("webhook -p 8082 stop")
    run("webhook -p 8082 ps", expect_error=True)


async def test_cli_two_start_stop(run):
    run("webhook -d -l DEBUG -T start")
    run("webhook -p 8081 -d -l DEBUG -T start")

    ret = run("webhook ps")
    lines = as_lines(ret.stdout)
    [info(line) for line in lines]
    assert len(lines) == 1

    ret = run("webhook -p 8081 ps")
    lines = as_lines(ret.stdout)
    [info(line) for line in lines]
    assert len(lines) == 1

    run("webhook ps")
    await Webhook().stop()
    run("webhook ps", expect_error=True)

    run("webhook -p 8081 ps")
    await Webhook(port=8081).stop()
    run("webhook -p 8081 ps", expect_error=True)


async def test_cli_debug_log(run, shared_datadir):
    logfile = shared_datadir / "webhook_test.log"
    os.environ["WEBHOOK_LOG_LEVEL"] = "DEBUG"
    os.environ["WEBHOOK_DEBUG"] = "1"
    os.environ["WEBHOOK_LOG_FILE"] = str(logfile)
    run("webhook ps", expect_error=True)
    run("webhook -T start")
    run("webhook ps")
    assert logfile.is_file()
    assert logfile.stat().st_size != 0
    await Webhook().stop()
