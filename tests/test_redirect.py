# -*- coding: utf-8 -*-
import sys

from cmdline import redirect_stdout


def test_redirect_stdout(capsys):
    # verify that all works as it should
    print('hello to stdout')
    print('hello to stderr', file=sys.stderr)
    captured = capsys.readouterr()
    assert captured.out == 'hello to stdout\n'
    assert captured.err == 'hello to stderr\n'

    # now redirect stdout -> stderr
    with redirect_stdout(sys.stderr):
        print('This is redirected to stderr')

    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == 'This is redirected to stderr\n'
