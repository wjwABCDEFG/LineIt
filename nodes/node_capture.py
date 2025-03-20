# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:54
@Author  : wenjiawei
"""
from datetime import datetime

from lt_conf import register_node
from lt_dev_mgr import dev_mgr
from nodes.node_base import BaseNode


@register_node("SCREEN_CAPTURE")
class NodeCapture(BaseNode):
    icon = "icons/capture.png"
    op_code = "SCREEN_CAPTURE"
    op_title = "截屏"
    content_label_objname = "node_capture"   # 这是样式qss名称

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, ])

    def evalImplementation(self, *args, **kwargs):
        if len(args) > 0:
            devices = [args[0], ]
        else:
            devices = dev_mgr.android_devs
        for dev in devices:
            dev_mgr.captureScreen(dev, f'./cache/screen_cap/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.png')

        self.markDirty(False)
        self.markInvalid(False)
        self.grNode.setToolTip("capture success")
        self.markDescendantsDirty()
        self.evalChildren()
        return self.value
