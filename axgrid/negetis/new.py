# coding:utf-8

import click
import os
import sys
from shutil import copytree
import glob
from .log import get_logger, init_logger
import i18n

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
    path = os.path.join(os.path.abspath(os.path.dirname(config.name)), "theme", name)
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
@click.argument('name')
def gettheme(config, verbose, name_or_path):
    pass


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



