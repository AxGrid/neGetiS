# coding:utf-8

from .log import get_logger, fatal
import i18n
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, contextfunction
import re
import codecs
import markdown
import yaml
from .extensions import Extensions
from .menu import Menu
from .tagextender import TagExtender
from asq import query

_ = i18n.t
log = get_logger()


class Processor(object):
    re_mark_doc = re.compile("^---\n(?P<meta>.*?)---(\n(?P<content>.*)|)$", re.MULTILINE | re.DOTALL)
    re_split = re.compile("^---SPLIT---$", re.MULTILINE | re.DOTALL)

    def __init__(self, config):
        self.config = config
        self.menu = Menu(self.config)
        try:
            log.debug("add loaders %s" % self.config.theme_path + "/layouts/")
            loader = ChoiceLoader([
                FileSystemLoader(self.config.theme_path + "/layouts/default/"),
                FileSystemLoader(self.config.theme_path + "/layouts/partials/"),
                FileSystemLoader(self.config.theme_path + "/layouts/")
            ])
            self.env = Environment(loader=loader)
            self.extensions = Extensions(self.config, self.env, self)

        except Exception as e:
            fatal("create environment exception %s" % e)

    def process(self, file_path, url_path, lang=None, contents=[], static=[]):
        __params = {
            "config": self.config.data,
            "path": url_path,
            "file_path": file_path,
            "lang": lang,
            "static_paths": static,
            "menu": self.menu.get_menu(lang, url_path)
        }

        file_content = self.get_content(file_path, __params, lang)
        if not file_content:
            return None
        file_layout = file_content["meta"].get("layout", "default.html")

        template = self.env.get_template(file_layout)
        if not template:
            fatal("layout %s not found" % file_layout)

        __params["page"] = file_content
        return template.render(__params)

    @staticmethod
    def __markdown(text):
        return markdown.markdown(text, extensions=["extra", "attr_list"])

    def get_content(self, file_path, params, lang=None, skip_ignore=False):
        with codecs.open(file_path, mode="r", encoding="utf-8") as input_file:
            text = input_file.read()
        __template = self.env.from_string(text)
        text = __template.render(params)
        m = self.re_mark_doc.match(text)
        if m:
            meta = yaml.safe_load(m.groupdict().get("meta", ""))
            meta["type"] = "markdown"
            content = m.groupdict().get("content", "")
            contents = []
            if meta.get("ignore", False) and not skip_ignore:
                return None
            if content:
                extender = TagExtender(self.config, meta, self.env, params)
                contents = self.re_split.split(content)
                content = self.__markdown(content)
                content = extender.extend(content, lang)
                contents = query(contents).select(self.__markdown).select(lambda x: extender.extend(x, lang)).to_list()

            return {"meta": meta, "content": content, "contents": contents}
        else:
            return {"meta": {"type": "text"}, "content": text, "contents": [text]}
