# coding:utf-8

import click
import os
from os.path import join, dirname
import sys
from shutil import copytree, rmtree, move, copyfile
from glob import glob
from .log import get_logger, fatal
from .processor import Processor
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
                log.debug("clear %s" % config.build["target"])
                rmtree(config.build["target"])
            if os.path.exists(config.build["static"]):
                log.debug("clear %s" % config.build["static"])
                rmtree(config.build["static"])
        self.processor = Processor(self.config)

    def collect_static(self):
        languages = self.config.get_all_languages_keys()
        log.debug("language count %d" % len(languages))
        for lang in languages:
            log.debug("collect static for lang %s" % lang)
            self.__collect_static(lang=lang)

    def __collect_static(self, lang=None):
        os.makedirs(self.config.build["static"], exist_ok=True)
        for (static_prefix, static_folder) in self.config.get_static(lang=lang):
            to = self.config.get_static_part_root(lang, static_prefix)
            log.debug("copy %s to %s" % (static_folder, to))
            copy_tree(static_folder, to)

    def collect_content(self):
        languages = self.config.get_all_languages_keys()
        for lang in languages:
            log.debug("collect content for lang %s" % lang or "default")
            if self.config.is_different_content_root: # TODO: это не разный конент а разные target
                self.__collect_content_different_root_mode(lang=lang)
            else:
                self.__collect_content(lang=lang)

    def __collect_content_different_root_mode(self, lang=None):
        os.makedirs(self.config.build["target"], exist_ok=True)
        content_folder = self.config.get_content_root(lang)
        for item in glob(content_folder+"/**/*", recursive=True):
            item_path = item.replace(content_folder, "")

            if self.config.is_different_target_root:
                to = join(self.config.build["target"],  self.config.get_language_variable("target", self.config.config, lang, lang + "/"))
            else:
                if self.config.default_language == lang:
                    to = self.config.build["target"]
                else:
                    to = join(self.config.build["target"], lang + "/")

            if os.path.isdir(item):
                print("DIR  ", item_path, "to", join(to, item_path))
            if os.path.isfile(item):
                if item.endswith(".md"):
                    only_file_name = os.path.splitext(os.path.basename(item))[0]
                    only_dir = os.path.dirname(item_path)
                    html_path = join(to, only_dir, only_file_name) + ".html"
                    log.debug("process content file %s to %s" % (item, html_path))
                    content = self.processor.process(item, item_path, lang)
                    os.makedirs(join(to, only_dir), exist_ok=True)
                    with open(html_path, "w") as html_file:
                        html_file.write(content)
                else:
                    log.debug("process media file %s to %s" % (item, join(to, item_path)))
                    os.makedirs(dirname(join(to, item_path)), exist_ok=True)
                    copyfile(item, join(to, item_path))

    def __collect_content(self, lang=None):
        os.makedirs(self.config.build["target"], exist_ok=True)
        pass



