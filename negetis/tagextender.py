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

    def replace(self, html):
        page = lxml.html.fromstring(html)
        for div in page.findall('.//div'):
            div.classes.add("my-class")

        for p in page.findall('.//p'):
            div.classes.add("my-class")


        for h1 in page.findall('.//h1'):
            h1.classes.add("my-class-h1")

        return lxml.etree.tostring(page)
