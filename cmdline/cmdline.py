# -*- coding: utf-8 -*-
"""
Partial command line parser
Purpose: add switches with actions to an existing command line processor

Accepts an array of options with members as follows:
"""
import sys
from typing import NamedTuple, Sequence, Dict, Any
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
    fn: Any = None


def system_args(options: Sequence[Option], *, process: callable = None,
                error: callable = None, results: dict = None) -> Dict:
    """
    Parse the command line args and partially process them
    :param options: sequence of options to parse
    :param process: process function
    :param error: error function
    :param results: optional dict to contain results (alternative to process callable)
    :return: parsed results, remaining unprocessed arguments
    """
    prog, args = sys.argv[0], sys.argv[1:]
    if results is None:
        results = {}
    if process:
        process(None, prog, args)
    else:
        results.setdefault('prog', prog)
    results, args = cmdline_args(args, options, process=process, error=error, results=results)
    sys.argv = [prog] + list(args)
    return results


def cmdline_args(argv: Sequence[str], options: Sequence[Option], *, process: callable = None,
                 error: callable = None, results: dict = None) -> (Dict, Sequence[str]):
    """
    Take an array of command line args, process them
    :param argv: argument array
    :param options: sequence of options to parse
    :param process: process function
    :param error: error function
    :param results: optional dict to contain results (alternative to process callable)
    :return: parsed results, remaining unprocessed arguments
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
                if short_opt:
                    error(f"unknown short option '-{short_opt}'")
                else:
                    error(f"unknown long option  '--{long_opt}'")
        return selected_option

    def dispatch_option(_option: Option, _opt: str, _args):
        if _option.fn is not None:
            return _option.fn(_option, _opt, _args) if callable(_option.fn) else _option.fn
        if process:
            tmp = process(_option, _opt, _args)
            if tmp is not None:
                return tmp
        return _args if _option.has_arg else True

    if results is None:
        results = dict()

    index = skip_count = 0
    saved_args = []

    for index, arg in enumerate(argv):
        if skip_count:
            skip_count -= 1
        elif arg.startswith('--'):  # long arg
            skip_count = 0
            longopt = arg[2:]
            option = select_option(None, longopt)
            if option is None:
                saved_args.append(f"--{longopt}")
            else:
                args = None
                if option.has_arg:
                    if '=' in longopt:
                        longopt, args = longopt.split('=', maxsplit=1)
                    else:
                        skip_count += 1
                        args = argv[index + skip_count]
                results[option.long] = dispatch_option(option, longopt, args)
        elif arg.startswith('-'):
            skip_count = 0
            for opt in arg[1:]:
                option = select_option(opt, None)
                if option is None:
                    saved_args.append(f"-{opt}")
                else:
                    if option.has_arg:
                        skip_count += 1
                    args = argv[index + skip_count] if option.has_arg else None
                    results[option.long] = dispatch_option(option, opt, args)
        else:
            break
    return results, saved_args + [arg for arg in argv[index + skip_count:]]


@contextmanager
def redirect_stdout(stream):
    stdout, sys.stdout = sys.stdout, stream
    try:
        yield
    finally:
        sys.stdout.flush()
        sys.stdout = stdout


def add_pythonpath(*args, prepend=True):
    """
    Add a path to python search path, avoid duplication
    :param args: paths to add to python path
    :param prepend: if true, paths are inserted at the start, else appended
    :return:

    This relies on Python 3.6+ insertion order of builtin dict
    """
    # prepend args to python path if prepend
    pythonpath = {str(p): None for p in args} if prepend else {}
    # add the python path
    pythonpath.update({p: None for p in sys.path})
    # append args to end unless prepend
    pythonpath.update({} if prepend else {str(p): None for p in args})
    # convert back to a list
    sys.path = list(pythonpath.keys())
    # end return it
    return sys.path
