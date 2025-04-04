# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/19 23:10
@Author  : wenjiawei
"""

from lt_conf import register_node
from nodes.node_base import BaseNode


@register_node("Arg2Val")
class NodeArg2Val(BaseNode):
    icon = "icons/arg2val.png"
    op_code = "Arg2Val"
    op_title = "Arg2Val"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])

    def evalImplementation(self, *args, **kwargs):
        input_node = self.getInput(0)
        if not input_node:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None
        input_node.eval()     # 从这里进去，但是其实并不用这里的val值，而是用的父节点传下来的args
        if not self.isDirty() and not self.isInvalid():
            # print(f'{self.value} 不用执行啦')
            return self.value
        if not args:
            print('no args')
            return self.value
        self.value = args[0]
        self.markDirty(False)
        self.markInvalid(False)
        self.grNode.setToolTip("")
        self.evalChildren()
        return self.value

    def evalOperation(self, dev: str, *args) -> str:
        super().evalOperation()
