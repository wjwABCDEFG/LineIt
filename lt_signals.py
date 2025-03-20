# -*- coding: utf-8 -*-
"""
尽量少用嗷
@Time    : 2025/3/17 17:14
@Author  : wenjiawei
"""
from PySide6.QtCore import QObject, Signal


class GlobalSignal(QObject):
    pass


globalSignal = GlobalSignal()
