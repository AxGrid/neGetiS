# coding:utf-8

import click
import os
from .log import get_logger, fatal
import i18n
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, contextfunction
import re
import codecs
import markdown
import yaml

_ = i18n.t
log = get_logger()


class Processor(object):
    re_mark_doc = re.compile("^---\n(?P<meta>.*)---(\n(?P<content>.*)|)$", re.MULTILINE | re.DOTALL)

    def __init__(self, config):
        self.config = config
        try:
            log.debug("add loaders %s" % self.config.theme_path + "/layouts/")
            loader = ChoiceLoader([
                FileSystemLoader(self.config.theme_path + "/layouts/default/"),
                FileSystemLoader(self.config.theme_path + "/layouts/partials/"),
                FileSystemLoader(self.config.theme_path + "/layouts/")
            ])

            self.env = Environment(loader=loader)
        except Exception as e:
            fatal("create environment exception %s" % e)

    def process(self, file_path, lang=None, contents=[], static=[]):
        file_content = self.__get_content(file_path)
        file_layout = file_content["meta"].get("layout", "default.html")
        template = self.env.get_template(file_layout)
        if not template:
            fatal("layout %s not found" % file_layout)
        return template.render({
            "page": file_content,
            "config": self.config.data
        })

    def __get_content(self, file_path):
        with codecs.open(file_path, mode="r", encoding="utf-8") as input_file:
            text = input_file.read()
            input_file.close()
        m = self.re_mark_doc.match(text)
        if m:
            meta = yaml.safe_load(m.groupdict().get("meta", ""))
            meta["type"] = "markdown"
            content = markdown.markdown(m.groupdict().get("content", ""))
            return {"meta": meta, "content": content}
        else:
            return {"meta": {"type": "text"}, "content": text}
