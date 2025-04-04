# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:54
@Author  : wenjiawei
"""
from datetime import datetime

from lt_conf import register_node
from utils.lt_dev_mgr import dev_mgr
from nodes.node_base import BaseNode


@register_node("SCREEN_CAPTURE")
class NodeCapture(BaseNode):
    icon = "icons/capture.png"
    op_code = "SCREEN_CAPTURE"
    op_title = "截屏"
    content_label_objname = "node_capture"   # 这是样式qss名称

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, ])

    def evalOperation(self, *args):
        dev = self.getInput(0).value
        dev_mgr.captureScreen(dev, f'./cache/screen_cap/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.png')
        self.grNode.setToolTip("capture success")
        return dev
