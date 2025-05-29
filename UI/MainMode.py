# coding=utf-8
import os

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
import maya.cmds as cmds
import pymel.core as pm
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance

#设置导入的函数命令



#maya的窗口指针指令
mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)  # 获得Maya主窗口


#撤销的装饰器
def undoChunk_wrapper(fn):  # wrapper 装饰器的名字，fn被装饰的函数（形参）
    # inner：被返回的函数，用来代替原函数
    def inner(*args, **kwargs):  # *args，**kwargs给原函数同样的参数配置
        """植入你想在执行目标函数之前要做的事情"""
        cmds.undoInfo(openChunk=True)
        ret = fn(*args, **kwargs)  # fn()是运行原函数，ret是原函数的返回值
        """植入你想在执行目标函数之后要做的事情"""
        cmds.undoInfo(closeChunk=True)
        return ret  # 将原函数的运行结果返回给调用方，在调用方看来，得到的结果韩式原函数的结果

    return inner  # 用来代替原函数

#UI窗口类
class BlendShapeTool(QWidget):  # 继承编译好的.py类

    def __init__(self, *args, **kwargs):
        super(BlendShapeTool, self).__init__(*args, **kwargs)
        self.setupUi(self)  # 运行父类初始化方法

        try:
            cmds.deleteUI('Tool')
        except RuntimeError:
            pass
        self.copy_connectAttr = None
        self.setObjectName("Tool")
        self.setParent(mayaMainWindow)  # 将新窗口设置为maya的子级
        self.setWindowFlags(Qt.Window)
        self.setWindow()

    #初始设置窗口的参数
    def setWindow(self):
        self.setConnect()  # 设置链接槽函数

    #设置窗口的
    def setConnect(self):
        pass





def show():
    ui = BlendShapeTool()
    ui.show()
    return ui


if __name__ == '__main__':
    show()
