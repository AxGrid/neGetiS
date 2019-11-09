# coding:utf-8

import click
import os
import sys
from shutil import copytree, rmtree, move
import glob
from .log import get_logger, init_logger
import i18n
import subprocess
import yaml
from .config import Config
from .builder import Builder

_ = i18n.t
log = get_logger()

__EXECUTABLE_PATH__ = os.getcwd()
__CURRENT_PATH__ = os.path.dirname(os.path.abspath(__file__))
__RESOURCE_PATH__ = os.path.join(__CURRENT_PATH__, "resources/")


@click.group()
def cli():
    pass


@cli.command(help=_("build_help"))
@click.option('verbose', '--verbose', is_flag=True, default=False, help=_("show_verbose"))
@click.option('target', '--target', default=None, help=_("build_opt_target"))
@click.option('clear', '--clear', is_flag=True, default=False, help=_("build_opt_clear"))
@click.option('config', '--config', default="./config.yaml", help=_("path_to_config"),
              type=click.File(mode="r"))
def build(verbose, target, clear, config):
    init_logger(verbose)
    config = Config(config)
    builder = Builder(config, target, clear)
    builder.collect_static()
    builder.collect_content()





