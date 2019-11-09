# coding:utf-8

import click
import os
from os.path import join, dirname, isabs
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
    def __init__(self, config, target, clear):
        self.config = config
        target = target or "public/"

        if not isabs(target):
            target = join(self.config.path, target)

        self.config.build["target"] = target
        if clear:
            if os.path.exists(config.build["target"]):
                log.debug("clear %s" % config.build["target"])
                rmtree(config.build["target"])
        self.processor = Processor(self.config)

    def collect_static(self):
        languages = self.config.get_all_languages_keys()
        log.debug("language count %d" % len(languages))
        for lang in languages:
            self.__collect_static(lang=lang)

    def __collect_static(self, lang=None):
        static_root = self.config.get_static_part_root(lang)
        log.debug("collect static for lang %s to %s", lang, static_root)

        #os.makedirs(self.config.build["static"], exist_ok=True)
        os.makedirs(static_root, exist_ok=True)
        for (static_prefix, static_folder) in self.config.get_static(lang=lang):
            to = self.config.get_static_part_root(lang, static_prefix)
            log.debug("copy %s to %s" % (static_folder, to))
            copy_tree(static_folder, to)

    def collect_content(self):
        languages = self.config.get_all_languages_keys()
        for lang in languages:
            log.debug("collect content for lang %s" % lang or "default")
            if self.config.is_different_content_root:
                self.__collect_content_different_content_root_mode(lang=lang)
            else:
                self.__collect_content_different_content_root_mode(lang=lang)

    def __collect_content_different_content_root_mode(self, lang=None):
        """
        Контент находится в разных каталогах content/en content/ru
        :param lang:
        :return:
        """
        os.makedirs(self.config.build["target"], exist_ok=True)
        content_folder = self.config.get_content_root(lang)
        for item in glob(content_folder+"/**/*", recursive=True):
            item_path = item.replace(content_folder, "")
            to = self.config.get_target_part_root(lang)

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

    def __collect_content_no_different_content_root_mode(self, lang=None):
        to = self.config.get_target_part_root(lang)
        os.makedirs(to, exist_ok=True)

        pass



