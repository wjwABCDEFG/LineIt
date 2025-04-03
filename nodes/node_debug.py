# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/19 23:10
@Author  : wenjiawei
"""

from lt_conf import register_node
from nodes.node_base import BaseNode


@register_node("DEBUG")
class NodeDebug(BaseNode):
    icon = "icons/debug.png"
    op_code = "DEBUG"
    op_title = "DEBUG"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])

    def evalOperation(self, *args):
        val = self.getInput(0).value
        print(f'DEBUG: {val}')
        return val
