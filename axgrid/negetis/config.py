# coding:utf-8

import os
from os.path import join, isdir, isfile, exists, isabs
import yaml
from deepmerge import always_merger
import glob
from asq import query
from copy import deepcopy
import i18n
import re

from .log import get_logger, fatal

_ = i18n.t
log = get_logger()


class Config:
    """
    Описывает конфигурационный фаил
    """

    def __init__(self, config_file):
        self.config_file = config_file
        self.path = os.path.abspath(os.path.dirname(config_file.name))
        self.config = yaml.safe_load(config_file)
        if not self.config.get("theme"):
            fatal(_("theme_not_set"))
        self.theme_path = join(self.path, "themes/", self.config["theme"])

        self.build = {}
        if not exists(join(self.theme_path, "theme.yaml")):
            fatal(_("theme_not_found"))

        with open(join(self.theme_path, "theme.yaml"), "r") as yaml_file:
            self.theme_config = yaml.safe_load(yaml_file)
            yaml_file.close()

        self.theme_config = {
            "data": self.theme_config.get("data", {}),
            "languages": self.theme_config.get("languages", {}),
            "menu": self.theme_config.get("menu", {}),
            "title": self.theme_config.get("title", None),
            "static": self.theme_config.get("static", "static/"),
            "static2": self.theme_config.get("static2", None),
            "static3": self.theme_config.get("static3", None),
        }
        self.data = self.merge(self.theme_config, self.config)
        self.default_language = self.data.get("defaultLanguage", "")
        # check modes
        self.is_different_content_root = query(self.data.get("languages", {}).items()).any(lambda x: "content" in x[1])
        if self.is_different_content_root:
            log.info("content different root mode")
            for wrong_language in query(self.data.get("languages", {}).items())\
                    .where(lambda x: "content" not in x[1])\
                    .select(lambda x: x[0]).to_list():
                log.warning("not set language.%s.content for content different root mode" % wrong_language)

        re_keys = query(self.get_all_languages_keys()).aggregate(lambda a, b: a+"|"+b)

        self.is_different_target_root = query(self.data.get("languages", {}).items()).any(lambda x: "target" in x[1])
        if self.is_different_target_root:
            log.info("target different root mode")
            for wrong_language in query(self.data.get("languages", {}).items())\
                    .where(lambda x: "target" not in x[1])\
                    .select(lambda x: x[0]).to_list():
                log.warning("not set language.%s.target for target different root mode" % wrong_language)

        if len(re_keys) == 0:
            self.re_content_multi_language_folder = re.compile("(?P<name>.*)$")
            self.re_content_multi_language_content = re.compile("(?P<name>.*)\\.(?P<ext>\\w+)$")
        else:
            self.re_content_multi_language_folder = re.compile("(?P<name>.*)\\.(?P<lang>[%s])$" % re_keys)
            self.re_content_multi_language_content = re.compile("(?P<name>.*)\\.(?P<lang>[%s])\\.(?P<ext>\\w+)$" % re_keys)
        # Mode:

    def __append_path(self, path):
        if os.path.isabs(path):
            return path
        else:
            return join(self.path, path)

    def get_static_part_root(self, lang=None, prefix=None):

        static_prefix = prefix or '' if lang == self.default_language else lang

        if self.is_different_target_root and not lang:
            return ''
        default = join(lang, "static/") if self.is_different_target_root else "static/"
        static_root = self.get_language_variable("static_target", self.config, lang, default)

        if not isabs(static_root):
            static_root = join(self.build["target"], static_root)

        if not lang:
            return static_root

        if self.is_different_target_root:
            return static_root
            # return join(static_root,
            #             self.get_language_variable("target", self.config, lang, lang + "/"))
        else:
            return join(static_root, static_prefix)



    @staticmethod
    def merge(a, b):
        _a = deepcopy(a)
        return always_merger.merge(_a, b)

    def get_content_root(self, lang=None):
        return self.__append_path(self.get_language_variable("content", self.config, lang, "content/"))

    def get_target_part_root(self, lang=None):
        if self.is_different_target_root:
            return join(self.build["target"], self.get_language_variable("target", self.config, lang, lang + "/"))
        else:
            if self.default_language == lang:
                return self.build["target"]
            else:
                return join(self.build["target"], lang + "/")

    @staticmethod
    def __get_sub_data(config, lang=None, data_root_path=None, __data={}):
        if "data" in config:
            __data = Config.merge(__data, config["data"])
        if "languages" in config and lang in config["languages"] and \
                "data" in config["languages"][lang]:
            __data = Config.merge(__data, config["languages"][lang]["data"])

        if data_root_path and exists(data_root_path):
            files = glob.glob(data_root_path + "*.yaml")
            if lang:
                files += glob.glob(data_root_path + "*.{lang}.yaml".format(lang=lang))
                for file_path in files:
                    with open(file_path, 'r') as yaml_file:
                        __data = Config.merge(__data, yaml.safe_load(yaml_file))
                        yaml_file.close()
        return __data

    def get_data(self, lang=""):
        __data = self.__get_sub_data(self.theme_config, lang,
                                     join(self.path, "themes/", self.config["theme"], "/data/"))
        __data = self.__get_sub_data(self.config, lang, join(self.path, "/data/"), __data)
        return __data

    @staticmethod
    def __merge_menu(data, new_data):
        q = query(new_data).contains
        __data = query(data).where(lambda x: not q(x, lambda a, b: a.get("name", "") == b.get("name", ""))).to_list()
        return query(Config.merge(__data, new_data)).order_by(lambda x: x.get("weight", 999)).to_list()

    def __get_sub_menu(self, config, lang=None, __data={}):
        if "menu" in config:
            __data = self.__merge_menu(__data, config["menu"])
        if "languages" in config and lang in config["languages"] and \
                "menu" in config["languages"][lang]:
            __data = self.__merge_menu(__data, config["languages"][lang]["menu"])
        return __data

    def get_menu(self, lang=None):
        __data = self.__get_sub_menu(self.theme_config, lang)
        __data = self.__get_sub_menu(self.config, lang, __data)
        return __data

    @staticmethod
    def get_language_variable(name, config, lang=None, default=None):
        __data = config.get(name, default)
        if "languages" in config and lang in config["languages"] and \
                name in config["languages"][lang]:
            __data = config["languages"][lang][name]
        return __data

    @staticmethod
    def __get_sub(key, config, lang=None, __data={}):
        if key in config:
            __data = Config.merge(__data, config[key])
        if "languages" in config and lang in config["languages"] and \
                key in config["languages"][lang]:
            __data = Config.merge(__data, config["languages"][lang][key])
        return __data

    @staticmethod
    def __get_sub_as_array(key, config, lang=None, __data={}):
        if key in config:
            if __data is None:
                __data = []
            if config[key]:
                item = config[key] if isinstance(config[key], list) or isinstance(config[key], dict) else [config[key]]
                __data = Config.merge(__data, item)
        if "languages" in config and lang in config["languages"] and \
                key in config["languages"][lang]:
            if __data is None:
                __data = []
            if config["languages"][lang][key]:
                item = config["languages"][lang][key] if isinstance(config["languages"][lang][key], list) or \
                                                         isinstance(config["languages"][lang][key], dict) else \
                    [config["languages"][lang][key]]
                __data = Config.merge(__data, item)
        return __data




    @staticmethod
    def __get_sub_as_static_array(key, config, lang, __data):
        def __merge(current_item, data_array, current_lang=""):
            data_array = data_array or []
            if isinstance(current_item, list):
                res = query(current_item).select(lambda x: (current_lang, x)).to_list()
            elif isinstance(current_item, str):
                res = (current_lang, current_item)
            else:
                res = None
            return data_array if res is None else Config.merge(data_array, res)

        if key in config:
            if __data is None:
                __data = []
            if config[key]:
                __item = config[key] if isinstance(config[key], list) or isinstance(config[key], dict) \
                    else [config[key]]
                __data = __merge(__item, __data, "")
        if "languages" in config and lang in config["languages"] and \
                key in config["languages"][lang]:
            if __data is None:
                __data = []
            if config["languages"][lang][key]:
                __item = config["languages"][lang][key] if isinstance(config["languages"][lang][key], list) or \
                                                           isinstance(config["languages"][lang][key], dict) else \
                                                           [config["languages"][lang][key]]

                __data = __merge(__item, __data, lang)
        return __data

    def get_static(self, lang=None):
        def __lam_path_join(path):
            return lambda x: (lambda a, b: (a, os.path.join(path, b)))(*x)

        def __collect_helper(config, language, path):
            __data = self.__get_sub_as_static_array("static", config, language, None)
            if __data is None:
                __data = [("", "static/")]
            __data = self.__get_sub_as_static_array("static2", config, language, __data)
            __data = self.__get_sub_as_static_array("static3", config, language, __data)
            return query(__data).select(__lam_path_join(path)).to_list()

        log.debug("read static %s" % self.theme_config)
        static_data = Config.merge(__collect_helper(self.theme_config, lang, self.theme_path),
                                   __collect_helper(self.config,       lang, self.path))
        log.debug("static %s" % static_data)
        return static_data

    def get_all_languages(self):
        """
        получить все основные языки
        :return:
        """
        languages = self.data.get("languages")
        if len(languages) == 0:
            return {self.default_language: {
                "name": self.default_language,
                "url": "/",
            }}
        else:
            return languages

    def get_all_languages_keys(self):
        """
        :return: список всех ключей
        """
        return list(self.get_all_languages().keys())

    # noinspection PyDictCreation
    def get_dict(self, lang=None):
        res = {
            "site": {},  # Сайт Глобальные данные
            "page": {},  # Текущая страница.md
            "menu": {},  # Меню
            "data": {},  # Дополнительные данные
            "static": {},  # Сататичные файлы
            "media": {},  # Медиа объекты
            # global
            "name": "",
            "title": "",  # Заголовок сайта
            "description": "",  # Описание сайта
            "languages": {}  # Языки
        }

        res["name"] = self.data.get("name", "")
        res["title"] = self.data.get("title", res["name"])
        res["description"] = self.data.get("description", "")
        res["site"]["title"] = self.get_language_variable("title", self.config, lang,
                                                          self.get_language_variable("title", self.theme_config, lang,
                                                                                     ""))
        res["site"]["description"] = self.get_language_variable("description", self.config, lang,
                                                                self.get_language_variable("description",
                                                                                           self.theme_config, lang, ""))
        res["data"] = self.get_data(lang)
        res["menu"] = self.get_menu(lang)
        res["languages"] = self.data.get("languages",
                                         {"default": {
                                             "name": "default",
                                             "url": "/"
                                         }})
        if lang in res["languages"]:
            # noinspection PyTypeChecker
            res["languages"][lang]["active"] = True
        res["languages_keys"] = list(res["languages"].keys())
        return res
