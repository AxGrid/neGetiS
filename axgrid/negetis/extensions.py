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

        # /<lang>/path.file
        # /path.<lang>.file
        # /path.file

        if self.config.is_different_target_root:
            __path = normpath(self.relativity_different_target(path, dirname(context["path"]), lang))
        else:
            __path = normpath(self.relativity_single_target(path, dirname(context["path"]), lang))

        log.debug("result %s static(%s) = %s" % (context["path"], path, __path))
        # print("PATH:", __path)
        # print("DIR :", dirname(context["path"]))
        # print("JOIN:", self.__join(self.config.build["target"], dirname(context["path"])))
        # print("REL :", relpath(__path, self.__join(self.config.build["target"], dirname(context["path"]))))

        if self.config.is_different_target_root:
            to = join(self.config.build["target"],
                      self.config.get_language_variable("target", self.config.config, lang, lang + "/"))
        else:
            if self.config.default_language == lang:
                to = self.config.build["target"]
            else:
                to = join(self.config.build["target"], lang + "/")

        return relpath(__path, self.__join(to, dirname(context["path"])))

        # #to = self.config.get_static_part_root(lang)
        #
        # if isabs(path):
        #     to = join(to, dirname(path))
        #     log.debug("absolute static(%s) = %s" % (path, to))
        # else:
        #     to = context.get("path", "./")
        #     log.debug("relative static(%s + %s) = %s" % (dirname(context["path"]),  path, to))
        #     path = join(dirname(context["path"]), path)

        # if self.config.is_different_target_root:
        #     return path

        # log.debug("result static(%s) = %s" % (path, path))
        # return path

    @staticmethod
    def __relativity(path):
        return "./"+path

    @staticmethod
    def __join(*args):
        return normpath(join(*args))

    def relativity_different_target(self, file_url, page_url, lang=None):
        if isabs(file_url):
            return join(self.config.get_static_part_root(lang), file_url)
        else:
            return join(self.config.get_static_part_root(lang), page_url, file_url)

    def relativity_single_target(self, file_url_path, page_url, lang=None):
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

        statics = [self.config.get_static_part_root(lang), self.config.build["static"]]
        if not isabs(file_url_path):
            file_url_path = self.__join(page_url, file_url_path)

        #if isabs(file_url_path):
        for path in statics:
            __result = __search(path, self.__relativity(file_url_path))
            if __result:
                return __result
        return join(self.config.build["static"], self.__relativity(file_url_path))










