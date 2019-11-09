# coding:utf-8

import os
from os.path import relpath, join, isabs, dirname, exists, normpath
import sys
from .log import get_logger, fatal
import i18n
from jinja2 import contextfunction
from os.path import relpath
from asq import query

_ = i18n.t
log = get_logger()


class Extensions(object):
    """
    Расширения шаблонного двига
    """
    def __init__(self, config, env):
        self.config = config
        self.env = env
        self.env.globals["static"] = self.static

    @contextfunction
    def static(self, context, path):
        lang = context.get("lang", self.config.default_language)
        if self.config.is_different_target_root:
            __path = normpath(self.relativity_different_target(path, dirname(context["path"]), lang))
        else:
            __path = normpath(self.relativity_single_target(path, dirname(context["path"]), lang))
        log.debug("result %s static(%s) = %s" % (context["path"], path, __path))
        to = self.config.get_target_part_root(lang)
        return relpath(__path, self.__join(to, dirname(context["path"])))

    @staticmethod
    def __relativity(path):
        return "./"+path

    @staticmethod
    def __join(*args):
        return normpath(join(*args))

    def __static_search_paths(self, lang):
        return [self.config.get_static_part_root(lang),
                self.config.get_target_part_root(lang),
                self.config.get_static_part_root()
                ]

    def __file_abs(self, file_url_path, page_url):
        return file_url_path if isabs(file_url_path) else self.__join(page_url, file_url_path)

    def relativity_different_target(self, file_url_path, page_url, lang=None):
        """
        Отстраивает контент для разных целей /ru/ /en/ ...
        :param file_url_path:
        :param page_url:
        :param lang:
        :return:
        """
        def __search(static_path, file_name):
            print ("__search ", path, self.__relativity(file_url_path))

            __path = join(static_path, lang, file_name)
            if exists(__path):
                return __path
            __path = join(static_path, file_name)
            if exists(__path):
                return __path
            return None
        file_url_path = self.__file_abs(file_url_path, page_url)
        for path in self.__static_search_paths(lang):
            __result = __search(path, self.__relativity(file_url_path))
            if __result:
                return __result
        return join(self.config.get_static_part_root(), self.__relativity(file_url_path))

    def relativity_single_target(self, file_url_path, page_url, lang=None):
        """
        Отстраивает контент для единой цели / /en/
        :param file_url_path:
        :param page_url:
        :param lang:
        :return:
        """
        def __search(static_path, file_name):
            __path = join(static_path, lang, file_name)
            if exists(__path):
                return __path
            (name, ext) = os.path.splitext(file_name)
            __path = join(static_path, "%s.%s.%s" % (name, lang, ext))
            if exists(__path):
                return __path
            __path = join(static_path, "%s-%s.%s" % (name, lang, ext))
            if exists(__path):
                return __path
            __path = join(static_path, file_name)
            if exists(__path):
                return __path
            return None

        file_url_path = self.__file_abs(file_url_path, page_url)

        for path in self.__static_search_paths(lang):
            __result = __search(path, self.__relativity(file_url_path))
            if __result:
                return __result
        return join(self.config.get_static_part_root(), self.__relativity(file_url_path))










