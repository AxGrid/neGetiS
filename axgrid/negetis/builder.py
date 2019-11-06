# coding:utf-8

import click
import os
import sys
from shutil import copytree, rmtree, move
import glob
from .log import get_logger, fatal
import i18n
from distutils.dir_util import copy_tree

_ = i18n.t
log = get_logger()


class Builder(object):
    def __init__(self, config, target, static, clear):
        self.config = config
        target = target or os.path.join(config.path, "public/")
        static = static or target
        config.build["target"] = target
        config.build["static"] = static
        if clear:
            if os.path.exists(config.build["target"]):
                rmtree(config.build["target"])
            if os.path.exists(config.build["static"]):
                rmtree(config.build["static"])

    def collect_static(self):
        languages = self.config.get_all_languages_keys()
        log.debug("language count %d" % len(languages))
        for lang in languages:
            log.debug("collect static for lang %s" % lang)
            self.__collect_static(lang=lang)

    def __collect_static(self, lang=None):
        os.makedirs(self.config.build["static"], exist_ok=True)
        for static_folder in self.config.get_static(lang=lang):
            log.debug("copy %s to %s" % (static_folder, self.config.build["static"],))
            copy_tree(static_folder, self.config.build["static"])

    def collect_content(self):
        pass