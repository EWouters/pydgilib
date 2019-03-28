"""This module holds the automated tests for atprogram."""

from atprogram.atprogram import (atprogram, get_device_info, get_project_size)
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
@pytest.mark.parametrize("verify", (False,))
# @pytest.mark.parametrize("verify",
#                          (pytest.param(True, marks=pytest.mark.xfail), False))
@pytest.mark.parametrize("return_output", (True, False))
@pytest.mark.parametrize("dry_run", (True, False))
def test_atprogram(
        verbose, clean, build, erase, program, verify, return_output, dry_run):
    """test_atprogram."""
    result = atprogram(
        project_path=project_path, verbose=verbose, clean=clean, build=build,
        erase=erase, program=program, verify=verify,
        return_output=return_output, dry_run=dry_run)
    assert not result or (return_output and result[-1] == '0')


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


def test_get_device_info():
    """test_get_device_info."""
    info = get_device_info(verbose=2)
    assert isinstance(info, dict)
    assert info.keys() == set(('Target voltage', 'Device information',
                               'Memory Information'))
    assert 'Name' in info['Device information']
    assert info['Memory Information'].keys() == set((['base', 'fuses']))


def test_get_project_size():
    """test_get_project_size."""
    atprogram(project_path=project_path, clean=False, build=True,
              erase=False, program=False, verify=False)
    size = get_project_size(project_path, verbose=2)
    assert isinstance(size, dict)
    size_keys = ('text', 'data', 'bss', 'dec', 'hex', 'filename')
    assert size.keys() == set(size_keys)
    for key in size_keys[:-1]:
        assert isinstance(size[key], int)
