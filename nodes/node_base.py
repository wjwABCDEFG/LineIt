import builtins
import re

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QLabel

from utils.lt_ui_switch import ToggleSwitch
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_node import Node
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER
from nodeeditor.utils_no_qt import dumpException
from utils.util_simple import throwException, type_to_color

DEBUG = False


class BaseGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 55
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def initAssets(self):
        super().initAssets()
        self.icons = QImage("icons/status_icons.png")

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )


class BaseNodeContent(QDMNodeContentWidget):
    def initUI(self):
        lbl = QLabel(self.node.content_label, self)
        lbl.setObjectName(self.node.content_label_objname)


class BaseNode(Node):
    icon = ""
    op_code = 0
    op_title = "Undefined"
    content_label = ""
    content_label_objname = "node_bg"   # 这是样式qss名称

    GraphicsNode_class = BaseGraphicsNode
    NodeContent_class = BaseNodeContent

    def __init__(self, scene, inputs=[0, 1], outputs=[2]):
        inputs, outputs = self.guessSocketType(inputs, outputs)
        super().__init__(scene, self.__class__.op_title, inputs, outputs)

        self.value = None       # 用于存储当前节点计算结果
        self.switch = None      # 开关QWidget
        self.detailsInfo = []   # details面板显示的信息，必须是list[QWidget]
        self.createDetailsInfo()
        self.markDirty()        # 一开始是dirty的，因为dirty才可以允许eval

    def initInnerClasses(self):     # AAA
        self.content = self.__class__.NodeContent_class(self)
        self.grNode = self.__class__.GraphicsNode_class(self)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def guessSocketType(self, need_inputs, need_outputs) -> (list, list):
        """
        非强制性解析socket类型并标注颜色
        通过解析evalOperation的注释来完成
        1: typehint类型标注def func(param1: str): -> dict
        2: 三引号注释中的:return: dict xxxx
        :return: (inputs, outputs)
        """
        inputs, outputs = need_inputs, need_outputs

        # 先按typehint解析
        in_idx = 0
        annos = self.__class__.evalOperation.__annotations__
        if annos:
            for anno, type_cls in annos.items():
                if anno == 'return':
                    outputs[0] = type_to_color(type_cls)    # output节点在这里只有一个
                else:
                    inputs[in_idx] = type_to_color(type_cls)
                    in_idx += 1
            return inputs, outputs

        # 再按三引号注释解析
        doc = self.__class__.evalOperation.__doc__
        if doc:
            match = re.search(r':return:\s*(\w+)', doc)
            if match:
                type_str = match.group(1)
                type_obj = getattr(builtins, type_str, None)
                outputs[0] = type_to_color(type_obj)

        return inputs, outputs

    def createDetailsInfo(self):
        self.switch = ToggleSwitch()
        self.detailsInfo.append(self.switch)

    def evalOperation(self, *args):
        """
        需要子类实现，本来是重写evalImplementation的，但是重复固定代码太多了，又抽了一层
        input/output类还是实现evalImplementation无需实现这个
        """
        return self.value

    def evalImplementation(self, *args, **kwargs):
        """
        原来的实现存在bug，先递归计算了父节点的eval，随后在计算evalChildren，但是父节点也进行了evalChildren，导致同一个节点会被计算n次
        如果设计成往前计算又会导致分叉无法计算
        这里设计成线往前找到顶，再执行evalChildren
        """
        ins = self.getInputs()

        if not ins:
            # 如果这里发现连接有问题，把后续所有节点都置为dirty
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        input_vals = []
        for input_node in ins:
            input_vals.append(input_node.eval())
            if not self.isDirty() and not self.isInvalid():
                # 这里要再判断一次，原来的代码只在eval判断，有问题，流程上是:
                # eval/Implementation->evalInput(父节点)->evalOperation(本节点)->evalChildren(子节点)
                # 但是在evalInput的时候，内部又会出发对当前节点的evalOperation，此时还没有值，执行了一次evalOperation
                # 调用栈跳回来后，此时本节点已经计算过，但又已经过了eval的检查，就会再执行一次
                # 因此如果不在这里判断，那么会执行多次
                # 修改后的流程为:
                # eval/Implementation->evalInput(父节点)->再次判断->evalOperation(本节点)->evalChildren(子节点)
                return self.value
            if not self.switch.isChecked():
                val = input_node.value
            else:
                val = self.evalOperation(input_vals)
            self.value = val    # 计算完成，存入当前value，这是很重要的一步，下个节点就可以从这里拿值，也是一个cache
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")

            # self.markDescendantsDirty()
            self.evalChildren()

            return val

    def eval(self, *args, **kwargs):
        """这里只是一些是否执行和执行异常判断，真正实现计算在evalImplementation"""
        if not self.isDirty() and not self.isInvalid():
            if DEBUG: print(" _> returning cached %s value:" % self.__class__.__name__, self.value)   # 如果已经是√状态就不再计算了，拿缓存
            return self.value

        try:
            val = self.evalImplementation(*args, **kwargs)
            return val
        except ValueError as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))      # 值类型错误通过状态和悬浮提示来提示用户，不需要dumpException在控制台显示错误
            self.markDescendantsDirty()
        except Exception as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            dumpException(e)

    def onInputChanged(self, socket=None):
        if DEBUG: print("%s::__onInputChanged" % self.__class__.__name__)
        self.markDirty()
        # self.eval()   # 这里不要连线自动计算了

    @throwException
    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        res['details_info'] = {'state': self.switch.isChecked()}
        return res

    @throwException
    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        self.switch.setCheckState(Qt.CheckState.Checked if data['details_info']['state'] else Qt.CheckState.Unchecked)
        if DEBUG: print("Deserialized CalcNode '%s'" % self.__class__.__name__, "res:", res)
        return res
