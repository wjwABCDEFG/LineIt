# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:55
@Author  : wenjiawei
"""

from PySide6.QtCharts import QSplineSeries, QValueAxis, QChart, QChartView
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPen, QPainter
from PySide6.QtWidgets import *

from lt_conf import register_node
from lt_dev_mgr import dev_mgr
from nodes.node_base import BaseNode


@register_node("PERF")
class NodePerf(BaseNode):
    icon = "icons/performance.png"
    op_code = "PERF"
    op_title = "性能数据"
    content_label_objname = "node_perf"   # 这是样式qss名称

    def __init__(self, scene):
        self.ui_package_name = None
        super().__init__(scene, inputs=[1], outputs=[1])

    def createDetailsInfo(self):
        self.detailsInfo = []

        group = QGroupBox('Params')
        group_layout = QVBoxLayout(group)

        # 包名行
        line_layout = QHBoxLayout()
        label = QLabel("包名")
        self.ui_package_name = QLineEdit()
        line_layout.addWidget(label)
        line_layout.addWidget(self.ui_package_name)
        group_layout.addLayout(line_layout)

        self.detailsInfo.append(group)

    def evalOperation(self, *args):
        devices = self.getInput(0).value
        package_name = self.ui_package_name.text()

        # TODO 后续并行化调整
        for dev in devices:
            chart = PerfChart(dev, package_name)
            chart.setTitle("FPS帧率")
            chart.legend().hide()
            chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.new_window = QWidget()
            self.new_window.setWindowTitle(f'{dev}-{package_name}')
            self.new_window.setGeometry(200, 200, 500, 400)
            layout = QVBoxLayout(self.new_window)
            layout.addWidget(chart_view)
            self.new_window.show()

        return self.value


class PerfChart(QChart):
    def __init__(self, dev_id, package_name, parent=None):
        super().__init__(QChart.ChartTypeCartesian, parent, Qt.WindowFlags())
        self._timer = QTimer()
        self._series = QSplineSeries(self)
        self._titles = []
        self._axisX = QValueAxis()
        self._axisY = QValueAxis()
        self._x = 0
        self._y = 0
        self.dev_id = dev_id
        self.package_name = package_name
        self.data = []

        green = QPen(Qt.red)
        green.setWidth(3)
        self._series.setPen(green)
        self._series.append(self._x, self._y)

        self.addSeries(self._series)
        self.addAxis(self._axisX, Qt.AlignBottom)
        self.addAxis(self._axisY, Qt.AlignLeft)

        self._series.attachAxis(self._axisX)
        self._series.attachAxis(self._axisY)
        self._axisX.setTickCount(5)
        self._axisX.setRange(-5, 5)
        self._axisY.setRange(0, 300)

        # 创建子线程收集数据
        self.collector_thread = DataCollectorThread(dev_id, package_name)
        self.collector_thread.data_ready.connect(self.handleTimeout)
        self.start_collection()

    def handleTimeout(self, data):
        x = self.plotArea().width() / self._axisX.tickCount()
        y = (self._axisX.max() - self._axisX.min()) / self._axisX.tickCount()
        self.data.append(data)
        self._x += y
        self._y = min(float(data['fps']), 300)
        self._series.append(self._x, self._y)
        self.scroll(x, 0)

    def start_collection(self):
        if not self.collector_thread.isRunning():
            self.collector_thread.start()

    def closeEvent(self, event):
        # 关闭窗口时停止线程
        self.collector_thread.stop()
        event.accept()


class DataCollectorThread(QThread):
    data_ready = Signal(object)

    def __init__(self, dev_id, package_name):
        super().__init__()
        self.dev_id = dev_id
        self.package_name = package_name
        self._is_running = True

    def run(self):
        while self._is_running:
            data = dev_mgr.monitor_performance(self.dev_id, self.package_name)
            self.data_ready.emit(data)
            self.msleep(1000)

    def stop(self):
        self._is_running = False
