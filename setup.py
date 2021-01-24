try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='cmdline',
    version=open('version').read().strip(),
    description='mini partial command line parser',
    author='David Nugent',
    author_email='david.nugent@news.com.au',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=[
        'cmdline',
    ],
)
