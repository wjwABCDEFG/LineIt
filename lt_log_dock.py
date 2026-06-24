# -*- coding: utf-8 -*-
"""
@Time    : 2026/6/24
@Author  : wenjiawei
日志输出窗口，重定向stdout/stderr
"""

import sys
from io import StringIO
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import *


class LogStream(StringIO):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def write(self, text):
        super().write(text)
        if text.strip():
            self.signal.emit(text)

    def flush(self):
        pass


class LineItLogDock(QWidget):
    append_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.redirect_output()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # 日志显示区域
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("QPlainTextEdit { background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace; font-size: 10pt; }")
        main_layout.addWidget(self.log_text)

        # 底部工具栏
        toolbar_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_log)
        toolbar_layout.addWidget(clear_btn)
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # 连接信号
        self.append_signal.connect(self.append_log)

    def redirect_output(self):
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

        sys.stdout = LogStream(self.append_signal)
        sys.stderr = LogStream(self.append_signal)

    def append_log(self, text):
        self.log_text.appendPlainText(text.strip())
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def clear_log(self):
        self.log_text.clear()

    def closeEvent(self, event):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        super().closeEvent(event)
