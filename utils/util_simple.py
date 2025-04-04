# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/31 1:24
@Author  : wenjiawei
"""
"""
字典美观打印
"""
from pprint import PrettyPrinter


pp = PrettyPrinter(indent=4).pprint


#############################################################################################
"""函数异常装饰器"""
from nodeeditor.utils_no_qt import dumpException


def throwException(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            dumpException(e)
            return {}
    return wrapper


#############################################################################################
"""
type -> color
"""
import hashlib
import colorsys


def type_to_color(type_obj):
    """
    将Python类型转换为十六进制颜色代码
    :param type_obj: 需要转换的类型对象
    :return: 格式为 '#RRGGBB' 的颜色代码
    """
    # 预定义常见类型的颜色（可根据需求扩展）
    predefined = {
        int: '#FF0000',     # 红色
        str: '#00FF00',     # 绿色
        list: '#0000FF',    # 蓝色
        dict: '#FF00FF',    # 品红
        float: '#FFFF00',   # 黄色
        bool: '#00FFFF',    # 青色
        tuple: '#FFA500',   # 橙色
        set: '#800080',     # 紫色
    }

    if type_obj in predefined:
        return predefined[type_obj]

    # 生成未预定义类型的颜色，通过HSL颜色空间生成更协调的颜色
    type_name = type_obj.__name__.encode('utf-8')
    hash_hex = hashlib.md5(type_name).hexdigest()

    hash_int = int(hash_hex, 16)
    hue = (hash_int % 360) / 360.0  # 色相分布在0-360度
    saturation = 0.7  # 固定饱和度70%
    lightness = 0.5  # 固定亮度50%

    # 将HLS转换为RGB
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)

    return f'#{r:02x}{g:02x}{b:02x}'

#
# # 示例用法
# print(type_to_color(int))  # #FF0000
# print(type_to_color(str))  # #00FF00
# print(type_to_color(list))  # #0000FF
# print(type_to_color(dict))  # #FF00FF
# print(type_to_color(float))  # #FFFF00
#
#
# # 自定义类型示例
# class MyClass:
#     pass
#
#
# print(type_to_color(MyClass))  # 类似 #9d3d6e（基于类型名生成的唯一颜色）
