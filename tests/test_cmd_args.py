# -*- coding: utf-8 -*-
import pytest
from cmdline import Option, cmdline_args, system_args

@pytest.fixture
def options():
    return [
        Option('a', 'always'),
        Option('b', 'book', True),
        Option('c', 'calendar'),
        Option('d', 'date', True),
        Option('s', 'sign', True),
        Option('p', 'peak', True),
        Option('q', 'quiet'),
        Option('v', 'verbose'),
    ]

class BoundTest:

    def __init__(self):
        self.result_list = []

    def process(self, option: Option, optstr, arg=None):
        self.result_list.append((option, optstr, arg))

    def error(self, msg):
        raise ValueError(msg)


def test_cmd_args_tuple(options):
    argument_list = ('--book', 'hello world', '--calendar', '-ad', '2021-02-14', 'the', 'rest', '--help')
    instance = BoundTest()

    the_rest = cmdline_args(argument_list, options, instance.process, instance.error)

    assert (options[1], 'book', 'hello world') in instance.result_list
    assert len(instance.result_list) == 4
    assert isinstance(the_rest, tuple)
    assert the_rest == ('the', 'rest', '--help')


def test_cmd_args_list(options):
    argument_list = ['--sign', 'leo', '--peak', '-62db', '-ad', '2021-02-14', '--verb', '-q', 'and', 'the', 'rest', '--help']
    instance = BoundTest()

    the_rest = cmdline_args(argument_list, options, instance.process, instance.error)

    assert (options[4], 'sign', 'leo') in instance.result_list
    assert len(instance.result_list) == 6
    assert isinstance(the_rest, list)
    assert the_rest == ['and', 'the', 'rest', '--help']


def test_system_cmd(options):
    import sys
    argument_list = ('/bin/myscript', '--sign', 'leo', '--peak', '-62db', '-ad', '2021-02-14', '--verb', '-q', 'and', 'the', 'rest', '--help')
    instance = BoundTest()

    sys.argv = argument_list
    system_args(options, instance.process, instance.error)

    assert (options[4], 'sign', 'leo') in instance.result_list
    assert len(instance.result_list) == 7
    assert isinstance(sys.argv, tuple)
    assert sys.argv == ('/bin/myscript', 'and', 'the', 'rest', '--help')

