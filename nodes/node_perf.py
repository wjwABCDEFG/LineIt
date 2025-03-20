# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:55
@Author  : wenjiawei
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

from lt_conf import register_node
from nodes.node_base import BaseNode


@register_node("PERF")
class NodePerf(BaseNode):
    icon = "icons/performance.png"
    op_code = "PERF"
    op_title = "性能数据"
    content_label_objname = "node_perf"   # 这是样式qss名称

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, ])

    def evalImplementation(self, *args, **kwargs):
        graph1 = Graph()
        graph1.show()
        # self.scene.grScene.addWidget(graph1)

        self.markDirty(False)
        self.markInvalid(False)
        self.grNode.setToolTip("capture success")
        self.markDescendantsDirty()
        self.evalChildren()
        return self.value


class Graph(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 400)
        self.setWindowFlags(Qt.Fram)
