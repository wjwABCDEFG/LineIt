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
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils_no_qt import dumpException
from nodes.node_base import BaseNode


@register_node("PERF")
class NodePerf(BaseNode):
    icon = "icons/performance.png"
    op_code = "PERF"
    op_title = "性能数据"
    content_label_objname = "node_perf"   # 这是样式qss名称

    def __init__(self, scene):
        self.new_window = PerfWidget()
        self.ui_package_name = None
        super().__init__(scene, inputs=[1], outputs=[1])

    def createDetailsInfo(self):
        super().createDetailsInfo()
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
        dev_id = self.getInput(0).value
        package_name = self.ui_package_name.text()
        self.new_window.setCollectInfo(dev_id, package_name)
        self.new_window.start_collection()
        return dev_id

    # 重写Graph类的serialize/deserialize方法
    class NodeInputContent(QDMNodeContentWidget):

        def initUI(self):
            pass

        def serialize(self):
            res = super().serialize()
            res['value'] = self.node.ui_package_name.text()
            return res

        def deserialize(self, data, hashmap={}):
            res = super().deserialize(data, hashmap)
            try:
                value = data['value']
                self.node.ui_package_name.setText(value)
                return True & res
            except Exception as e:
                dumpException(e)
            return res

    NodeContent_class = NodeInputContent


class PerfWidget(QWidget):
    """
    多个chart的容器，每个PerfWidget对应一个设备的监控线程
    """
    chart_show = Signal(object)
    title_update = Signal(str)

    def __init__(self, dev_id='', package_name='', parent=None):
        super().__init__(parent)
        self.dev_id = dev_id
        self.package_name = package_name

        self.indicators = ['fps', 'memory_mb', 'cpu_percent']   # 性能指标
        self.indicators_range = [(0, 200), (0, 1024), (0, 100)]
        self.collector_thread = None

        self._layout = QVBoxLayout(self)
        self.setGeometry(0, 0, 500, 900)
        self.charts = {}
        self.setWindowTitle(f'{dev_id}-{package_name}')
        self.addCharts()
        self.show()

        self.title_update.connect(self.updateTitle)

    def updateTitle(self, title):
        self.setWindowTitle(title)

    def setCollectInfo(self, dev_id, package_name):
        self.dev_id = dev_id
        self.package_name = package_name
        self.title_update.emit(f'{dev_id}-{package_name}')

    def addCharts(self):
        for indicator in self.indicators:
            chart = PerfChart(indicator)
            chart.setTitle(indicator)
            chart.legend().hide()
            chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self._layout.addWidget(chart_view)
            self.charts[indicator] = chart

    def updateCharts(self, data: dict):
        for indicator, val in data.items():
            if indicator == 'timestamp':
                continue
            chart = self.charts[indicator]
            chart.handleTimeout(val)

    def start_collection(self):
        # 子线程开始收集数据
        self.collector_thread = DataCollectorThread(self.dev_id, self.package_name)
        self.collector_thread.data_ready.connect(self.updateCharts)
        if not self.collector_thread.isRunning():
            self.collector_thread.start()

    def closeEvent(self, event):
        # 关闭窗口时停止线程
        self.collector_thread.stop()
        event.accept()


class PerfChart(QChart):
    def __init__(self, indicator, parent=None):
        super().__init__(QChart.ChartTypeCartesian, parent, Qt.WindowFlags())
        self._timer = QTimer()
        self._series = QSplineSeries(self)
        self._titles = []
        self._axisX = QValueAxis()
        self._axisY = QValueAxis()
        self._x = 0
        self._y = 0
        self.indicator = indicator  # fps/cpu/memory
        self.data = []

        red = QPen(Qt.red)
        red.setWidth(3)
        self._series.setPen(red)
        self._series.append(self._x, self._y)

        self.addSeries(self._series)
        self.addAxis(self._axisX, Qt.AlignBottom)
        self.addAxis(self._axisY, Qt.AlignLeft)

        self._series.attachAxis(self._axisX)
        self._series.attachAxis(self._axisY)
        self._axisX.setTickCount(5)
        self._axisX.setRange(-5, 5)
        self._axisY.setRange(0, 100)

    def handleTimeout(self, data: int | float):
        self.data.append(data)
        self._axisY.setRange(int(min(self.data[-5:])) - 1, int(max(self.data[-5:])) + 1)
        x = self.plotArea().width() / self._axisX.tickCount()
        y = (self._axisX.max() - self._axisX.min()) / self._axisX.tickCount()
        self._x += y
        self._y = float(data)
        self._series.append(self._x, self._y)
        self.scroll(x, 0)


class DataCollectorThread(QThread):
    data_ready = Signal(object)

    def __init__(self, dev_id, package_name):
        super().__init__()
        self.dev_id = dev_id
        self.package_name = package_name
        self._is_running = True

    def run(self):
        dev_mgr.clear_fps(self.dev_id, self.package_name)
        while self._is_running:
            self.msleep(1000)
            data = dev_mgr.monitor_performance(self.dev_id, self.package_name)
            self.data_ready.emit(data)

    def stop(self):
        self._is_running = False
