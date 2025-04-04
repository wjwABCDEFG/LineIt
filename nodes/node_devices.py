# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/30 23:36
@Author  : wenjiawei
"""
from multiprocessing import Process
from threading import Thread

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import *

from lt_conf import register_node
from utils.lt_dev_mgr import dev_mgr
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodes.node_base import BaseNode


@register_node("FIND_DEVICE")
class NodeDevices(BaseNode):
    icon = "icons/device.png"
    op_code = "FIND_DEVICE"
    op_title = "设备列表"
    content_label_objname = "node_device"

    def __init__(self, scene):
        super().__init__(scene, inputs=[])
        dev_mgr.addDevChangedEventListener(self.onChanged)
        self.onChanged(None)        # 一开始先来一次
        self.process_list = []

    def onChanged(self, obj):
        val = {**dev_mgr.android_devs, **dev_mgr.ios_devs}
        self.value = val
        self.store_device = val
        self.content.deviceChanged.emit(val)

    def evalImplementation(self):
        self.markDirty(False)
        self.markInvalid(False)
        self.grNode.setToolTip("")
        for dev in self.value:
            self.markDescendantsDirty()
            t = Thread(target=self.evalChildren, args=(dev, ))
            self.process_list.append(t)
            t.start()
            t.join()
        return self.value

    class NodeDevicesOutputContent(QDMNodeContentWidget):
        deviceChanged = Signal(dict)

        def initUI(self):
            layout = QVBoxLayout(self)

            self.list_widget = QListWidget()
            self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            layout.addWidget(self.list_widget)

            self.deviceChanged.connect(self.formatContent)
            self.formatContent({**dev_mgr.android_devs, **dev_mgr.ios_devs})

        def update_list_height(self):
            # 计算内容总高度
            total_height = 0
            for i in range(self.list_widget.count()):
                total_height += self.list_widget.sizeHintForRow(i)

            # 添加边距
            margin = 2 * self.list_widget.frameWidth()  # 上下边框
            self.list_widget.setFixedHeight(total_height + margin)
            self.height = total_height + margin

        def formatContent(self, data):
            self.list_widget.clear()
            for dev in data.values():
                item = QListWidgetItem(f"{dev['brand']}-{dev['name']}")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsAutoTristate)
                self.list_widget.addItem(item)
            if len(data.values()) == 0:
                self.list_widget.addItem('NoDevices')
            self.update_list_height()

    NodeContent_class = NodeDevicesOutputContent
