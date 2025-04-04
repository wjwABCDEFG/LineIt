# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""
import os.path
import subprocess

from PySide6.QtWidgets import *

from lt_conf import register_node
from nodes.node_base import BaseNode
from utils.util_simple import throwException


@register_node("PYTHON")
class NodePython(BaseNode):
    icon = "icons/python.png"
    op_code = "PYTHON"
    op_title = "Python"

    def __init__(self, scene, inputs=[2], outputs=[1]):
        self.edit_app_name = None
        super().__init__(scene, inputs, outputs)

    def createDetailsInfo(self):
        super().createDetailsInfo()
        group = QGroupBox('PythonCode')
        group_layout = QVBoxLayout(group)

        self.ui_code = QPlainTextEdit()
        self.ui_code.setObjectName("myTextEdit")
        self.ui_code.setStyleSheet("QPlainTextEdit { color: white; }")
        group_layout.addWidget(self.ui_code)

        self.detailsInfo.append(group)

    def evalOperation(self, *args):
        code = self.ui_code.toPlainText()
        exec(code)
        return self.value

    def onDoubleClicked(self, event):
        try:
            _temp_file = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "_temp.py"))
            with open(_temp_file, 'w') as f:
                text = self.ui_code.toPlainText()
                f.write(text)

            cmd = f"code --wait {_temp_file}"
            proc = subprocess.Popen(cmd, shell=True)
            proc.wait()
            self.on_vscode_close(_temp_file)
        except subprocess.CalledProcessError as e:
            print(f"错误：无法启动 VS Code。请确保已配置 PATH。详细信息：{e}")
        except Exception as e:
            print(f"未知错误：{e}")

    def on_vscode_close(self, temp_file):
        print('vscode closed')
        try:
            with open(temp_file, 'r') as f:
                self.ui_code.setPlainText(f.read())
            os.remove(temp_file)
        except Exception as e:
            print(f"未知错误：{e}")

    @throwException
    def serialize(self):
        res = super().serialize()
        res['details_info']['code'] = self.ui_code.toPlainText()
        return res

    @throwException
    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap)
        value = data['details_info']['code']
        self.ui_code.setPlainText(value)
        return res
