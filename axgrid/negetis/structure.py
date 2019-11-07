# coding:utf-8

from os.path import join
from glob import glob
import i18n
import re

from .log import get_logger, fatal

_ = i18n.t
log = get_logger()


class Structure(object):
    def __init__(self, config):
        self.config = config
        self.languages_keys = self.config.get_all_languages_keys()

        self.data = {}

    def collect(self):
        for lang in self.languages_keys:
            self.__collect(lang)

    def __collect(self, lang):
        content_root = self.config.get_content_root(lang)
        log.info("collect content for language %s content root %s" % (lang, content_root))
        pass
