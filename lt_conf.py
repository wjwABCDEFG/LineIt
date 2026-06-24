import importlib
import os
from os.path import dirname, isdir, join

LISTBOX_MIMETYPE = "application/x-item"


# 一开始NODES是空的，动态的往里面添加class，key是上面的op_code代表加减乘除，value是类，注意不是对象
LINEIT_NODES = {
}


class ConfException(Exception): pass
class InvalidNodeRegistration(ConfException): pass
class OpCodeNotRegistered(ConfException): pass


def register_node_now(op_code, class_reference):
    if op_code in LINEIT_NODES:
        raise InvalidNodeRegistration("Duplicate node registration of '%s'. There is already %s" %(
            op_code, LINEIT_NODES[op_code]
        ))
    LINEIT_NODES[op_code] = class_reference


def register_node(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class
    return decorator


def get_class_from_opcode(op_code):
    if op_code not in LINEIT_NODES: raise OpCodeNotRegistered("OpCode '%s' is not registered" % op_code)
    return LINEIT_NODES[op_code]


# import all nodes and register them
from nodes import *

# 动态import所有子包
nodes_dir = join(dirname(__file__), 'nodes')
for name in os.listdir(nodes_dir):
    pkg_path = join(nodes_dir, name)
    if isdir(pkg_path) and os.path.exists(join(pkg_path, '__init__.py')):
        mod = importlib.import_module(f'nodes.{name}')
        globals().update(vars(mod))
