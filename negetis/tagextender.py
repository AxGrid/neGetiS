# coding: utf-8

import lxml
from lxml.html import fromstring, tostring
from deepmerge import always_merger as merge
from .log import get_logger, fatal
import i18n

_ = i18n.t
log = get_logger()


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
    def __init__(self, config, meta, env, context={}):
        self.config = config
        self.meta = meta
        self.env = env
        self.context = context
        # TODO: Join tag_morph's

    def __transform(self, rules, key, item):
        params = merge.merge({
            "text": item.text,
            "classes": item.classes,
            "attrib": item.attrib,
            "meta": self.meta,

        }, self.context)

        log.info("%s" % params)
        log.info("%s" % item.text)
        log.info("%s" % params["text"])
        log.info("%s" % rules.get(key, ""))
        text = self.env.from_string(rules.get(key, "")).render(params)
        return fromstring("<out_temp>" + text + "</out_temp>")

    def __get_morphs(self, lang=None):
        if "morph" in self.meta:
            if isinstance(self.meta["morph"], str):
                morph = self.config.get_morph(lang)
                log.debug("morph is %s" % morph)
                morph = morph.get(self.meta["morph"])
            else:
                morph = self.meta["morph"]
            return morph
        return None

    def extend(self, html, lang=None):
        morph = self.__get_morphs(lang)
        if not morph or not len(morph):
            return html

        log.debug("morph found %s", morph)

        page = lxml.html.fromstring("<out_temp>" + html + "</out_temp>")
        for rules in morph:
            if "from" not in rules:
                continue

            log.debug("morph rules found %s" % rules)

            for item in page.findall('.//'+rules["from"]):
                log.debug("morph item %s" % item)
                if "classes" in rules:
                    log.debug("morph item.classes %s add %s" % (item.classes, rules["classes"]))
                    item.classes.add(rules["classes"])
                if "tag" in rules:
                    item.tag = rules["tag"]
                if "innerText" in rules:
                    item.text = rules["innerText"]
                if "render" in rules:
                    new_item = self.__transform(rules, "render", item)
                    item.getparent().replace(item, new_item)
                if "innerHtml" in rules:
                    new_item = self.__transform(rules, "innerHtml", item)
                    item.append(new_item)
                if "addPreviousHtml" in rules:
                    new_item = self.__transform(rules, "addPreviousHtml", item)
                    item.addprevious(new_item)
                if "addNextHtml" in rules:
                    new_item = self.__transform(rules, "addNextHtml", item)
                    item.addnext(new_item)

        page_text = tostring(page).decode('utf-8')
        log.debug("result page %s", page_text)
        return page_text.replace("<out_temp>", "").replace("</out_temp>", "")
