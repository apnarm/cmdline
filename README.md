# cmdline
- a tiny unsophisticated partial  command line parser

## Objective
This package was written to allow parsing of parts of a command line, just pre-commandline arguments to a command.

It is originally written as a front-end command pre-processor for arguments passed to Django's `manage.py`, not 
swallowing the entire command line but allowing some options to be parsed and actioned before the main show, 
without interfering with the specific command being executed.

This allows, for example, setting internal or environment variables, modifying or setting the 
DJANGO_SETTINGS_MODULE variable or any other use that can be imagined.

Parsing rules are a simplified version of what are accepted as POSIX rules for command line processing.
- Both short '-x' and long '--xoption' are supported
- Short options can be concatenated, but to avoid ambiguity any option that requires an argument are consumed
  consecutively from subsequent arguments and cannot be appended to the short opt itself
- The form --longopt=argument is supported
- Optional arguments are not supported 
- Evaluation order is significant and is exactly as specified on the command line.
- You can't mix arguments with command arguments, the parser quits when a command is encountered and
  preserves all arguments following that command

The Option class used in option specifications are NamedTuples which is very compact. 

Example (based on Django manage.py generated by cookiecutter-django):
 ```python3
#!/usr/bin/env python3
"""
Usage: manage.py [-e <env>] [-d] [-o] [-h] <other manage.py args>
  -e --env <environment>   set runtime environment local, production
  -d --docker              set internal configuration for docker
  -o --dotenv              enhanced configuration via .env
  -h --help                display this help
"""
import os
import sys
from cmdline import Option, system_args


if __name__ == "__main__":
    opts = [
        Option('e', 'env', has_arg=True),   # -e or --env switch
        Option('d', 'docker'),              # -d or --docker
        Option('o', 'dotenv'),              # -o or --dotenv
        Option('h', 'help'),                # -h or --help
    ]
    environ = 'local'   # default
    docker = False
    read_dotenv = '0'
    settings = dict(prog=sys.argv[0])

    def process_args(option: Option, key, arg):
        if not option:  # use 2nd arg to do something based on command invoked
            settings['prog'] = key
        elif option.short == 'e':
            settings['environ'] = arg
        elif option.short == 'd':
            settings['docker'] = True
        elif option.short == 'o':
            settings['read_dotenv'] = '1'
        elif option.short == 'h':
            print(__doc__)
            exit(0)

    def export(var, val):
        os.environ[var] = val

    system_args(opts, process_args)
    vars().update(settings)   

    default_settings = f'config.settings.{environ}'
    export('USE_DOCKER', 'yes' if docker else 'no')
    export('DOCKER_READ_DOT_ENV_FILE', read_dotenv)
            
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django  # noqa
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )

        raise

    execute_from_command_line(sys.argv)
```
