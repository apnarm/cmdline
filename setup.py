try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='cmdline',
    version='0.1.0',
    packages=[
        'cmdline',
    ],
)
