# coding:utf-8

from os.path import join, isabs
class Menu(object):
    def __init__(self, config):
        self.config = config

    def get_menu(self, lang=None, path="/", level=990):
        """
        Получить меню
        :param lang: язык
        :param path: путь, для построения active
        :param level: уровень вложенности
        :return: { menu structure }
        """

        def __strip(menu, strip_level, current_level=0):
            __res = []
            if strip_level <= current_level:
                return []
            for item in menu:
                if "children" in item:
                    item["children"] = __strip(item["children"], strip_level, current_level+1)
                __res += [item]
            return __res

        def __set_active(menu, path, current_path="/"):
            for item in menu:
                link = item.get("link","")
                if isabs(link):
                    if link == path:
                        item["active"] = True
                    continue
                link = join(current_path, link)
                if link == path:
                    item["active"] = True
                if "children" in item:
                    item["children"] = __set_active(item["children"], path, link)

        menu = self.config.get_menu(self, lang=lang) or []
        menu = __strip(menu, level)
        menu = __set_active(menu, path)
        return menu

    def get_breadcrumbs(self, lang=None, path="/"):
        """
        Получить путь
        :param lang: язык
        :param path: путь, для построения active
        :return: [{ path structure }, { path structure }...]
        """
        pass