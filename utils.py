# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/31 1:24
@Author  : wenjiawei
"""
from pprint import PrettyPrinter
from nodeeditor.utils_no_qt import dumpException


pp = PrettyPrinter(indent=4).pprint


def throwException(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            dumpException(e)
            return {}
    return wrapper
