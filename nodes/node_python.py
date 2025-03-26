# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""
import os.path
import subprocess

from PySide6.QtWidgets import *

from lt_conf import register_node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils_no_qt import dumpException
from nodes.node_base import BaseNode


@register_node("PYTHON")
class NodePython(BaseNode):
    icon = "icons/python.png"
    op_code = "PYTHON"
    op_title = "Python"

    def __init__(self, scene, inputs=[2], outputs=[1]):
        self.edit_app_name = None
        super().__init__(scene, inputs, outputs)

    def createDetailsInfo(self):
        self.detailsInfo = []

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

    # 重写Graph类的serialize/deserialize方法
    class NodeInputContent(QDMNodeContentWidget):

        def initUI(self):
            pass

        def serialize(self):
            res = super().serialize()
            res['value'] = self.node.ui_code.toPlainText()
            return res

        def deserialize(self, data, hashmap={}):
            res = super().deserialize(data, hashmap)
            try:
                value = data['value']
                self.node.ui_code.setPlainText(value)
                return True & res
            except Exception as e:
                dumpException(e)
            return res

    NodeContent_class = NodeInputContent
