"""This module holds the automated tests for atprogram."""

from atprogram.atprogram import atprogram
from os import path, getcwd
import pytest

project_path = path.join(getcwd(), "UnitTest", "UnitTest")


def test_atprogram_simple():
    """test_atprogram_simple."""
    assert 0 == atprogram(project_path=project_path,
                          clean=True, build=True, program=True)


# Can be passed to next test. Will be evaluated on printed output (stdout).
def _true(out):
    return True


@pytest.mark.parametrize(" returncode, func, kwargs", [
    # (0, _true, {}),
    (0, _true, dict(project_path=project_path)),
    # pytest.param(0, lambda stdout: True, {}, marks=pytest.mark.xfail),
])
@pytest.mark.parametrize("clean", (True, False))
@pytest.mark.parametrize("build", (True, False))
@pytest.mark.parametrize("erase", (True, False))
@pytest.mark.parametrize("program", (True, False))
@pytest.mark.parametrize("verbose", (0, 3))
# @pytest.mark.parametrize("verify", (False, pytest.param(
#     True, marks=pytest.mark.xfail)))
# @pytest.mark.parametrize("dry_run", (True, False))
def test_atprogram(capsys, returncode, func, kwargs, verbose, clean, build,
                   erase, program, verify=True, dry_run=True):
    """test_atprogram."""
    assert returncode == atprogram(
        **kwargs, verbose=verbose, clean=clean, build=build, erase=erase,
        program=program, verify=verify, dry_run=dry_run)
    out = capsys.readouterr().out
    print(out)
    assert func(out)


@pytest.mark.parametrize("make_command, atprogram_command", [
    ("--version", "--version"),
    (None, "--version"),
    ("--version", None),
    pytest.param(None, None, marks=pytest.mark.xfail(
        raises=ValueError), strict=True)])
def test_atprogram_command(make_command, atprogram_command):
    """test_atprogram_command."""
    assert 0 == atprogram(make_command=make_command,
                          atprogram_command=atprogram_command)
