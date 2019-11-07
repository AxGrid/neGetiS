# coding:utf-8

import click
import os
from os.path import join
import sys
from shutil import copytree, rmtree, move
import glob
from .log import get_logger, fatal
import i18n
from distutils.dir_util import copy_tree
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, contextfunction

_ = i18n.t
log = get_logger()


class Builder(object):
    def __init__(self, config, target, static, clear):
        self.config = config
        target = target or join(config.path, "public/")
        static = static or join(target, "static/")
        config.build["target"] = target
        config.build["static"] = static
        if clear:
            if os.path.exists(config.build["target"]):
                rmtree(config.build["target"])
            if os.path.exists(config.build["static"]):
                rmtree(config.build["static"])

        loader = ChoiceLoader([
            FileSystemLoader(self.config.theme_path + "/layouts/_default/"),
            FileSystemLoader(self.config.theme_path + "/layouts/partials/"),
            FileSystemLoader(self.config.theme_path + "/layouts/")
        ])
        self.env = Environment(loader=loader)

    def collect_static(self):
        languages = self.config.get_all_languages_keys()
        log.debug("language count %d" % len(languages))
        for lang in languages:
            log.debug("collect static for lang %s" % lang)
            self.__collect_static(lang=lang)

    def __collect_static(self, lang=None):
        os.makedirs(self.config.build["static"], exist_ok=True)
        for (static_prefix, static_folder) in self.config.get_static(lang=lang):
            to = join(self.config.build["static"], static_prefix)
            log.debug("copy %s to %s" % (static_folder, to))
            copy_tree(static_folder, to)

    def collect_content(self):
        languages = self.config.get_all_languages_keys()
        for lang in languages:
            log.debug("collect content for lang %s" % lang)
            self.__collect_content(lang=lang)

    def __collect_content(self, lang=None):
        os.makedirs(self.config.build["target"], exist_ok=True)
        pass


