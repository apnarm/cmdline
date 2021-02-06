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

@pytest.fixture
def options_fn():
    return [
        Option('a', 'always', fn=True),
        Option('b', 'book', has_arg=True),
        Option('c', 'calendar', fn=False),
        Option('d', 'date', has_arg=True),
        Option('s', 'sign', has_arg=True),
        Option('p', 'peak', has_arg=True),
        Option('q', 'quiet', fn=True),
        Option('v', 'verbose', fn=True),
    ]

@pytest.fixture
def defaults():
    return dict(
        always=False,
        book='default book',
        calendar=True,
        date='2000-01-02',
        sign='ares',
        peak='0db',
        quiet=False,
        verbose=False,
    )

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

    results, the_rest = cmdline_args(argument_list, options, process=instance.process, error=instance.error)

    assert (options[1], 'book', 'hello world') in instance.result_list
    assert len(instance.result_list) == 4
    assert isinstance(the_rest, list)
    assert the_rest == ['the', 'rest', '--help']


def test_cmd_args_list(options):
    argument_list = ['--sign', 'leo', '--peak=-62db', '-ad', '2021-02-14', '--verb', '-q', 'and', 'the', 'rest', '--help']
    instance = BoundTest()

    results, the_rest = cmdline_args(argument_list, options, process=instance.process, error=instance.error)

    assert (options[4], 'sign', 'leo') in instance.result_list
    assert (options[5], 'peak', '-62db') in instance.result_list
    assert len(instance.result_list) == 6
    assert isinstance(the_rest, list)
    assert the_rest == ['and', 'the', 'rest', '--help']

    assert isinstance(results, dict)


def test_cmd_args_results(options_fn, defaults):
    argument_list = ['--sign', 'leo', '--peak=-62db', '-ad', '2021-02-14', '--verb', '-q',
                     'and', 'the', 'rest', '--help']
    instance = BoundTest()

    results, the_rest = cmdline_args(argument_list, options_fn, error=instance.error)

    assert the_rest == ['and', 'the', 'rest', '--help']
    assert results == dict(sign='leo', peak='-62db', always=True, date='2021-02-14', verbose=True, quiet=True)

    results, the_rest = cmdline_args(argument_list, options_fn, error=instance.error, results=defaults.copy())

    assert results == dict(book='default book', calendar=True, sign='leo', peak='-62db', always=True,
                           date='2021-02-14', verbose=True, quiet=True)


def test_system_cmd(options):
    import sys
    argument_list = ('/bin/myscript', '--sign', 'leo', '--peak', '-62db', '-ad', '2021-02-14', '--verb', '-q',
                     'and', 'the', 'rest', '--help')
    instance = BoundTest()

    sys.argv = argument_list
    results = system_args(options, process=instance.process, error=instance.error)

    assert (options[4], 'sign', 'leo') in instance.result_list
    assert (options[5], 'peak', '-62db') in instance.result_list
    assert len(instance.result_list) == 7
    assert isinstance(sys.argv, list)
    assert sys.argv == ['/bin/myscript', 'and', 'the', 'rest', '--help']

    assert isinstance(results, dict)


def test_system_cmd_results(options_fn, defaults):
    import sys
    argument_list = ('/bin/myscript', '--sign', 'leo', '--peak', '-62db', '-ad', '2021-02-14', '--verb', '-q',
                     'and', 'the', 'rest', '--help')
    instance = BoundTest()

    sys.argv = argument_list
    results = system_args(options_fn, error=instance.error)

    assert isinstance(results, dict)
    assert sys.argv == ['/bin/myscript', 'and', 'the', 'rest', '--help']

    assert isinstance(results, dict)
    assert results == dict(prog='/bin/myscript', sign='leo', peak='-62db', always=True, date='2021-02-14',
                           verbose=True, quiet=True)

    sys.argv = argument_list
    results = system_args(options_fn, error=instance.error, results=defaults.copy())

    assert sys.argv == ['/bin/myscript', 'and', 'the', 'rest', '--help']
    assert results == dict(prog='/bin/myscript', book='default book', calendar=True, sign='leo', peak='-62db',
                           always=True, date='2021-02-14', verbose=True, quiet=True)
