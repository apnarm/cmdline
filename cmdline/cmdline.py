# -*- coding: utf-8 -*-
"""
Partial command line parser
Purpose: add switches with actions to a command line processor

Accepts an array of options with members as follows:
"""
from typing import NamedTuple, List, Callable

__all__ = (
    'Option',
    'cmdline_args',
    'system_args'
)


class Option(NamedTuple):
    short: str
    long: str
    hasarg: bool = False


def system_args(options: List[Option], process: Callable, error: Callable =None):
    import sys

    prog = sys.argv[0]
    argv = cmdline_args(sys.argv[1:], options, process, error)
    return [prog] + argv



def cmdline_args(argv, options: List[Option], process: Callable, error: Callable =None):
    """
    Take an array of command line args, process them
    :param argv: argument array
    :param process: process function
    :param error: error function
    :return: remaining unprocessed arguments
    """
    def select_option(shortopt, longopt):
        selected_option = None
        for option in options:
            if shortopt is not None and shortopt == option.short:
                selected_option = option
                break
            elif longopt is not None and option.long is not None and option.long.startswith(longopt):
                selected_option = option
                break
        else:
            if error is not None:
                error(f"unknown {'short' if shortopt else 'long'} option - '{shortopt if shortopt is not None else longopt}'")
        return selected_option


    index = 0
    skip_count = 0
    for index, arg in enumerate(argv):
        if skip_count:
            skip_count -= 1
        elif arg.startswith('--'):   # longarg
            skip_count = 0
            longopt = arg[2:]
            option = select_option(None, longopt)
            if option.hasarg:
                skip_count += 1
            process(option, longopt, argv[index+1] if option.hasarg else None)
        elif arg.startswith('-'):
            skip_count = 0
            for shortopt in arg[1:]:
                option = select_option(shortopt, None)
                if option.hasarg:
                    skip_count += 1
                process(option, shortopt, argv[index+skip_count] if option.hasarg else None)
        else:
            break
    return argv[index+skip_count:]
