"""This module holds the automated tests for atprogram."""

from atprogram.atprogram import atprogram
from os import path, getcwd
import pytest

project_path = path.join(getcwd(), "UnitTest", "UnitTest")


def test_atprogram_simple():
    """test_atprogram_simple."""
    assert not atprogram(project_path=project_path,
                         clean=True, build=True, program=True)


# @pytest.mark.parametrize("verbose", (0, 3))
@pytest.mark.parametrize("verbose", (3,))
# @pytest.mark.parametrize("clean", (True, False))
@pytest.mark.parametrize("clean", (False,))
@pytest.mark.parametrize("build", (True, False))
@pytest.mark.parametrize("erase, program",
                         [(False, False), (True, False), (True, True)])
@pytest.mark.parametrize("verify", (False, pytest.param(
    True, marks=pytest.mark.xfail)))
# @pytest.mark.parametrize("dry_run", (True, False))
@pytest.mark.parametrize("dry_run", (False,))
def test_atprogram(verbose, clean, build,
                   erase, program, verify, dry_run):
    """test_atprogram."""
    assert not atprogram(
        project_path=project_path, verbose=verbose, clean=clean, build=build,
        erase=erase, program=program, verify=verify, dry_run=dry_run)


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
