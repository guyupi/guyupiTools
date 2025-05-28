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

import uiDesigner.SkirtTool as UI
from ..utils.common import skirtTool
reload(UI)
reload(skirtTool)

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)  # 获得Maya主窗口



def undoChunk_wrapper(fn):    #wrapper 装饰器的名字，fn被装饰的函数（形参）
    #inner：被返回的函数，用来代替原函数
    def inner(*args,**kwargs):    #*args，**kwargs给原函数同样的参数配置
        """植入你想在执行目标函数之前要做的事情"""
        cmds.undoInfo(openChunk=True)
        ret = fn(*args,**kwargs)    #fn()是运行原函数，ret是原函数的返回值
        """植入你想在执行目标函数之后要做的事情"""
        cmds.undoInfo(closeChunk=True)
        return ret    #将原函数的运行结果返回给调用方，在调用方看来，得到的结果韩式原函数的结果
    return inner    #用来代替原函数


class SkirtTool(QWidget, UI.Ui_SkirtToolWin):  # 继承编译好的.py类

    def __init__(self, *args, **kwargs):
        # type: (SkirtTool, object) -> object
        super(SkirtTool, self).__init__(*args, **kwargs)

        self.skirtClass = None

        self.setupUi(self)  # 运行父类初始化方法
        try:
            cmds.deleteUI('SkirtTool')
        except RuntimeError:
            pass
        self.setObjectName("SkirtTool")
        self.setParent(mayaMainWindow)  # 将新窗口设置为maya的子级
        self.setWindowFlags(Qt.Window)
        self.setWindow()

    def setWindow(self):
        self.setConnect()  # 设置链接槽函数

    def setConnect(self):

        self.SkirtFrameBt.clicked.connect(self.create_SkirtClass)
        self.controlSysBt.clicked.connect(self.create_skirtJointCtrl)
        self.buildSkirtPolyBt.clicked.connect(self.create_skirtJM)

    @undoChunk_wrapper
    def create_SkirtClass(self):
        skirt_name = self.skirtlineEdit.text()
        if skirt_name == "" :
            skirt_name = "skirt"
        skirt = skirtTool.skirCommon(skirt_name)
        self.skirtClass = skirt
        spans = self.jointListNumSB.value()
        self.skirtClass.create_Frame(spans=spans)

    @undoChunk_wrapper
    def create_skirtJointCtrl(self):
        midJointNum = self.jointNumSB.value()

        if cmds.objExists(self.skirtClass.joint_grp) or cmds.objExists(self.skirtClass.ctrl_grp):

            cmds.delete(self.skirtClass.joint_grp , self.skirtClass.ctrl_grp)
            self.skirtClass.create_JointCon(midJointNum=midJointNum)
        else:
            self.skirtClass.create_JointCon(midJointNum=midJointNum)

    @undoChunk_wrapper
    def create_skirtJM(self):
        self.skirtClass.create_jianmo()


def show():
    ui = SkirtTool()
    ui.show()
    return ui

if __name__ == '__main__':
    show()








