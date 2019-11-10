# coding: utf-8

import re
import lxml
from lxml.html import fromstring


class TagExtender(object):
    """
    Модифицирует теги после марк дауна
    config:
        tag_morph:
            p:
                tag: div
                class: my-class
                attr:
                    "x-id":
                        - 15
                        - 17
            ".//code[@class=\"python\"]":
                tag: code
                class: my-class
                attr:
                    "x-id":
                        - 15
                        - 17

    """
    def __init__(self, config, meta):
        self.config = config
        self.meta = meta
        # TODO: Join tag_morph's


    def __build_morph(self, morph_name):
        morph = self.config.get_morph("morph").get(morph_name)
        if not morph:
            return None
        for item in morph:
            if "render" in item:
                item["render"] = lxml.html.fromstring(item["render"])
        return morph


    def replace(self, morph_name, html, lang=None):
        morph = self.__build_morph(morph_name)
        if not morph:
            return html

        page = lxml.html.fromstring(html)
        for div in page.findall('.//div'):
            div.classes.add("my-class")

        for p in page.findall('.//p'):
            div.classes.add("my-class")


        for h1 in page.findall('.//h1'):
            h1.classes.add("my-class-h1")

        return lxml.html.tostring(page)
