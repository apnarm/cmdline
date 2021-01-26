# -*- coding: utf-8 -*-
"""
Partial command line parser
Purpose: add switches with actions to an existing command line processor

Accepts an array of options with members as follows:
"""
import sys
from typing import NamedTuple, Sequence, Callable
from contextlib import contextmanager


__all__ = (
    'Option',
    'cmdline_args',
    'system_args',
    'redirect_stdout',
    'add_pythonpath',
)


class Option(NamedTuple):
    short: str
    long: str
    has_arg: bool = False


def system_args(options: Sequence[Option], process: Callable, error: Callable = None):
    prog = sys.argv[0]
    args = sys.argv[1:]
    process(None, prog, args)
    args = cmdline_args(args, options, process, error)
    sys.argv = tuple([prog] + list(args))


def cmdline_args(argv: Sequence[str], options: Sequence[Option], process: Callable, error: Callable = None) \
        -> Sequence[str]:
    """
    Take an array of command line args, process them
    :param argv: argument array
    :param options: sequence of options to parse
    :param process: process function
    :param error: error function
    :return: remaining unprocessed arguments
    """

    def select_option(short_opt, long_opt):
        selected_option = None
        for current_opt in options:
            if short_opt is not None and short_opt == current_opt.short:
                selected_option = current_opt
                break
            elif long_opt is not None and current_opt.long is not None:
                if current_opt.long.startswith(long_opt) or long_opt.startswith(current_opt.long):
                    selected_option = current_opt
                    break
        else:
            if error is not None:
                error(f"unknown {'short' if short_opt else 'long'} option - "
                      f"'{short_opt if short_opt is not None else long_opt}'")
        return selected_option

    index = 0
    skip_count = 0
    for index, arg in enumerate(argv):
        if skip_count:
            skip_count -= 1
        elif arg.startswith('--'):  # long arg
            skip_count = 0
            longopt = arg[2:]
            option = select_option(None, longopt)
            args = None
            if option.has_arg:
                if '=' in longopt:
                    longopt, args = longopt.split('=', maxsplit=1)
                else:
                    skip_count += 1
                    args = argv[index + skip_count]
            process(option, longopt, args)
        elif arg.startswith('-'):
            skip_count = 0
            for opt in arg[1:]:
                option = select_option(opt, None)
                if option.has_arg:
                    skip_count += 1
                process(option, opt, argv[index + skip_count] if option.has_arg else None)
        else:
            break
    return argv[index + skip_count:]


@contextmanager
def redirect_stdout(stream):
    stdout = sys.stdout
    sys.stdout = stream
    yield
    sys.stdout.flush()
    sys.stdout = stdout


def add_pythonpath(*args, prepend=True):
    pythonpath = {p: None for p in args} if prepend else {}
    pythonpath.update({p: None for p in sys.path})
    pythonpath.update({} if prepend else {p: None for p in args})
    sys.path = list(pythonpath.keys())
    return sys.path
