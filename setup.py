#!/usr/bin/env python

from setuptools import setup, find_namespace_packages

exec(open('axgrid/negetis/version.py').read())

setup(
    name='axgrid_negetis',
    version=__version__,
    description='Static site generator',
    author='Dmitry Vysochin',
    author_email='dmtiry.vysochin@gmail.com',
    url='https://github.com/negetis/',
    packages=find_namespace_packages(include=['axgrid.*']),
    install_requires=[
        'Click',
        'Jinja2',
        'python-i18n[YAML]',
        'Werkzeug',
        'pytz',
        'deepmerge',
        'pyyaml-include',
        'markdown',
        'asq',
        'watchdog',
        'deprecation',
        'pillow',
        'python-thumbnails'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'negetis=axgrid.negetis.main:run'
        ]
    }
)