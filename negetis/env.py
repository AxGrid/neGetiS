# coding:utf-8

import os
from os.path import join, isdir, isfile, exists, isabs
import yaml
from .utils import merge
import glob
from asq import query
from copy import deepcopy
import i18n
import re

from axgridcommons import lenses
from axgridcommons.datafile import DataFile

from .log import get_logger, fatal

_ = i18n.t
log = get_logger()


class Env(object):
    """
    Окружение
    """

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = DataFile(config_file.name).data
        self.path = os.path.abspath(os.path.dirname(config_file.name))
        assert self.config.get("theme") is not None, "theme not set in config"
        self.theme_path = join(self.path, "themes/", self.config["theme"])
        self.theme_config = DataFile(join(self.theme_path, "theme.yaml")).data
        self.default_language = self.get("defaultLanguage")

        if self.get("languages") and len(self.get("languages").keys()) > 1:
            self.multi_language = True

        query(self.get("language", {}).items()).any(lambda x: "content" in x[1])
        self.is_different_content_root = query(self.get("language", {}).items()).any(lambda x: "content" in x[1])
        self.is_different_target_root = query(self.get("language", {}).items()).any(lambda x: "target" in x[1])

        self.__warnings()

    def __warnings(self):
        if self.is_different_content_root:
            for wrong_language in query(self.get("languages", {}).items()) \
                    .where(lambda x: "content" not in x[1]) \
                    .select(lambda x: x[0]).to_list():
                log.warning("not set language.%s.content for content different root mode" % wrong_language)
        if self.is_different_target_root:
            log.info("target different root mode")
            for wrong_language in query(self.get("languages", {}).items()) \
                    .where(lambda x: "target" not in x[1])\
                    .select(lambda x: x[0]).to_list():
                log.warning("not set language.%s.target for target different root mode" % wrong_language)

    @property
    def language(self):
        return self.default_language

    def lang(self, lang=None):
        return Language(self, lang)

    def get(self, key, default=None):
        return self.lang(self.default_language).get(key, default)

    def get_lang(self, key, default=None):
        return self.lang(self.default_language).get_lang(key, default)

    def get_root(self, key, default=None):
        return self.lang(self.default_language).get_root(key, default)


class Language:
    def __init__(self, evn, lang=None):
        self.env = evn
        self.lang = lang
        self.lang_root = "language." + self.lang + "." if lang else None
        self.is_different_content_root = self.env.is_different_content_root
        self.is_different_target_root = self.env.is_different_target_root

    @property
    def language(self):
        return self.lang

    def get(self, key, default=None):
        if self.lang_root:
            return lenses.get(self.env.config, self.lang_root + key,
                              lenses.get(self.env.config, key,
                                         lenses.get(self.env.theme_config, self.lang_root + key,
                                                    lenses.get(self.env.theme_config, key, default)
                                                    )
                                         )
                              )
        else:
            return self.get_root(key, default)

    def get_lang(self, key, default=None):
        if self.lang_root:
            return lenses.get(self.env.config, self.lang_root + key, lenses.get(self.env.theme_config, self.lang_root + key, default))
        return default

    def get_root(self, key, default=None):
        return lenses.get(self.env.config, key, lenses.get(self.env.theme_config, key, default))


class Menu:
    def __init__(self, env):
        self.env = env


class Static(object):
    def __init__(self, env):
        self.env = env

    def collect(self):
        """
        :return: возвращает пути для сбора статики
        """
        res = []
        for (static_key, default) in [("static", None), ("static2", None), ("static3", None)]:
            k = self.env.get_lang(static_key, default)
            if k:
                res.append((self.env.language, k))

        for (static_key, default) in [("static", "./static"), ("static2", None), ("static3", None)]:
            k = self.env.get_root(static_key, default)
            if k:
                res.append(('', k))

