# coding:utf-8

import unittest
import os
from os.path import join
from axgrid.negetis.config import Config
import tracemalloc
from asq import query


__CURRENT_PATH__ = os.path.dirname(os.path.abspath(__file__))
__RESOURCES__ = join(__CURRENT_PATH__, "resources/")


class TestAxGridConfigStatic(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tracemalloc.start()

    def __read_config(self, name):
        with open(join(__RESOURCES__, name), "r") as config_file:
            cfg = Config(config_file)
            self.assertIsNotNone(cfg)
            return cfg

    @staticmethod
    def __any(static, path_part, lang=''):
        return query(static).any(lambda x: (lambda a, b: a == lang and b.endswith(path_part))(*x))

    def test_config_static_basic(self):
        config = self.__read_config("config-basic.yaml")
        static = config.get_static()
        self.assertIsNotNone(static)
        self.assertEqual(static[0], ('', join(__RESOURCES__, "themes/", "test/", "static/")))
        self.assertEqual(static[1], ('', join(__RESOURCES__, "static/")))

    def test_config_static_multi_language(self):
        config = self.__read_config("config-lang.yaml")
        self.assertTrue(len(config.get_all_languages_keys()) > 1)
        static = config.get_static("ru")
        self.assertTrue(self.__any(static, 'resources/themes/test/static/'))
        self.assertFalse(self.__any(static, 'resources/static/'))
        self.assertTrue(self.__any(static, 'resources/static/ru/', 'ru'))
        self.assertTrue(self.__any(static, 'resources/static2/ru2/', 'ru'))

    def test_config_content_basic(self):
        config = self.__read_config("config-basic.yaml")
        self.assertTrue(len(config.get_all_languages_keys()) == 1)
        content = config.get_content_root()
        self.assertEqual(content, join(__RESOURCES__, "content/"))

    def test_config_content_multi_language(self):
        config = self.__read_config("config-lang.yaml")
        self.assertTrue(len(config.get_all_languages_keys()) > 1)
        content = config.get_content_root("ru")
        self.assertEqual(content, join(__RESOURCES__, "content/", "ru/"))
        content = config.get_content_root()
        self.assertEqual(content, join(__RESOURCES__, "content/"))


if __name__ == '__main__':
    unittest.main()

