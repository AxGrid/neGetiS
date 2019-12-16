# coding:utf-8

from deepmerge import always_merger
from copy import deepcopy


def merge(a, b):
    _a = deepcopy(a)
    return always_merger.merge(_a, b)
