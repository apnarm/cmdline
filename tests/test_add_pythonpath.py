# -*- coding: utf-8 -*-
import sys
from pathlib import Path

import pytest
from cmdline import add_pythonpath


def test_add_pythonpath():
    # add nothing, ensure nothing has changed
    original_path = sys.path[:]
    add_pythonpath()
    try:
        assert original_path == sys.path
    except AssertionError:
        print(f'sys.path contained duplicate entries {len(original_path)} => {len(sys.path)}', file=sys.stderr)

    # add current (test) module's parent
    tests = Path(__file__).resolve().parent
    testdir = str(tests)
    add_pythonpath(testdir, prepend=True)
    assert len(sys.path) == len(original_path) + (1 if testdir not in original_path else 0)
    assert sys.path[0] == testdir

    # add a directory which should not be present
    home = str(Path.home())
    add_pythonpath(home, prepend=False)
    assert len(sys.path) == len(original_path) + 1
    assert sys.path[-1] == home
