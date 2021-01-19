# cmdline
- a tiny unsophisticated "partial" command line parser

## Objective
This package was written to allow parsing of parts of a command line,
just pre-arguments to a command.

It was written as a front-end pre-processor for arguments passed to Django's `manage.py`,
not swallowing the entire command but allowing some options to be parsed and action before
the main show, without interfering with the specific command being executed.
This allows, for example, setting internal or environment variables, modifying or setting
the DJANGO_SETTINGS_MODULE variable or any other use that can be imagined.

Example (based on manage.py generated by cookiecutter-django):
```python
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
        Option('e', 'env', hasarg=True),    # -e or --env switch
        Option('d', 'docker'),              # -d or --docker
        Option('o', 'dotenv'),              # -o or --dotenv
        Option('h', 'help'),                # -h or --help
    ]
    environ = 'local'   # default
    def process_args(option: Option, opt, arg):
        global environ
        if option.short == 'e':
            environ = arg
        elif option.short == 'd':
            os.environ['USE_DOCKER'] = 'true'
        elif option.short == 'o':
            os.environ['DJANGO_READ_DOT_ENV_FILE'] = '1'
        elif option.short == 'h':
            print(__doc__)
            exit(0)

    system_args(opts, process_args)
    default_settings = 'config.settings.' + environ
            
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