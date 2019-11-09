#!/usr/bin/env python
# coding:utf-8

import click
import os
import i18n
from .log import get_logger, init_logger
from .version import __version__

i18n.set('locale', 'ru')
i18n.set('file_format', 'yaml')
i18n.set('filename_format', '{locale}.{format}')
i18n.load_path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/", "i18n/"))

# for translations
from .new import cli as new_cli
from .build import cli as build_cli

_ = i18n.t
log = get_logger()


@click.group()
def cli():
    pass


@cli.command(help=_("version_help"))
@click.option('verbose', '--verbose', is_flag=True, default=False, help=_("show_verbose"))
def version(verbose):
    init_logger(verbose)
    log.debug("Static site generator")
    import pkg_resources
    try:
        my_version = pkg_resources.get_distribution('negetis').version
    except:
        my_version = "dev"
    log.info(_("version", ver=my_version))


def run():
    glob_cli = click.CommandCollection(sources=[new_cli, build_cli, cli])
    glob_cli(obj={})
