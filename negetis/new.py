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

_ = i18n.t
log = get_logger()

__EXECUTABLE_PATH__ = os.getcwd()
__CURRENT_PATH__ = os.path.dirname(os.path.abspath(__file__))
__RESOURCE_PATH__ = os.path.join(__CURRENT_PATH__, "resources/")


@click.group()
def cli():
    pass


@cli.command(help=_("site_help_newsite"))
@click.option('--path', help=_("site_help_folder"))
@click.option('verbose', '--verbose', is_flag=True, default=False, help=_("show_verbose"))
@click.argument('name')
def newsite(path, verbose, name):
    init_logger(verbose)

    if not name:
        fatal(_("site_set_name"))
    path = os.path.join(__EXECUTABLE_PATH__, name+"/") if not path else path
    log.debug("create new site path: %s" % path)
    if os.path.exists(path):
        fatal(_("site_path_already_exist", path=path, name=name))

    copytree(os.path.join(__RESOURCE_PATH__, "site/"), path)
    rm_placeholders(path)
    log.info(_("site_created", path=path))


@cli.command(help=_("theme_help_newtheme"))
@click.option('config', '--config', default="./config.yaml", help=_("path_to_config"),
              type=click.File(mode="r"))
@click.option('verbose', '--verbose', is_flag=True, default=False, help=_("show_verbose"))
@click.argument('name')
def newtheme(config, verbose, name):
    init_logger(verbose)
    if not name:
        fatal(_("theme_set_name"))
    path = os.path.join(os.path.abspath(os.path.dirname(config.name)), "themes", name)
    log.debug("create new theme path: %s" % path)
    if os.path.exists(path):
        fatal(_("theme_path_already_exist", path=path, name=name))

    copytree(os.path.join(__RESOURCE_PATH__, "theme/"), path)
    rm_placeholders(path)
    log.info(_("theme_created", path=path))


@cli.command(help=_("theme_help_getheme"))
@click.option('config', '--config', default="./config.yaml", help=_("path_to_config"),
              type=click.File(mode="r"))
@click.option('verbose', '--verbose', is_flag=True, default=False, help=_("show_verbose"))
@click.option('name', '--name', default=None, help="set new name of theme")
@click.argument('theme')
def gettheme(config, verbose, theme, name):
    init_logger(verbose)
    path = os.path.join(os.path.abspath(os.path.dirname(config.name)), "theme")
    temp_path = os.path.join(path, "__tmp")
    if os.path.exists(os.path.join(path, "__tmp")):
        rmtree(os.path.join(path, "__tmp"))

    cmd = "git clone %s %s" % (theme, temp_path)
    log.debug(cmd)
    data = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    log.debug(data)
    if os.path.exists(os.path.join(temp_path, "theme.yaml")):
        rmtree(os.path.join(path, "__tmp"))
        fatal(_("theme_wrong_repository"))

    if name:
        theme_name = name
    else:
        with open(os.path.join(temp_path, "theme.yaml")) as theme_config:
            theme_yaml = yaml.safe_load(theme_config)
            theme_name = theme_yaml.get("name", "unnamed")
    move(temp_path, os.path.join(path, theme_name))


def fatal(text):
    log.fatal(text)
    sys.exit(128)


def rm_placeholders(path):
    log.debug("delete placeholders at path %s" % path)
    for item in glob.glob(path+"/*"):
        if os.path.isdir(item):
            if os.path.exists(os.path.join(item, ".placeholder")):
                log.debug("delete %s" % item)
                os.remove(os.path.join(item, ".placeholder"))
            rm_placeholders(item)



