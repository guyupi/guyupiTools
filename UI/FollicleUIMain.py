#!/usr/bin/env python
# -*- coding: utf-8 -*-
import maya.cmds as cmds

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance


import uiDesigner.follicleTooUI as follicleUi
from ..utils.rigging import mesh
from ..utils.rigging import follicleUtils

reload(follicleUi)
reload(mesh)
reload(follicleUtils)
mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)



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


class FollicleTool(QWidget,follicleUi.Ui_FollicleTool):

    def __init__(self,*args, **kwargs):

        super(FollicleTool, self).__init__(*args, **kwargs)

        try:
            cmds.deleteUI('FollicleTool')
        except RuntimeError:
            pass
        self.setObjectName("FollicleTool")
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.setupUi(self)

        self.signalConnect()    #设置信号链接
        self.setWindow()        #设置窗口属性


    def setWindow(self):
        """
        窗口的相关设置
        :return: None
        """
        #设置创建简模的法线方向按钮ID
        self.buttonGroup.setId(self.planeYdirection,1)
        self.buttonGroup.setId(self.planeZdirection , 2)
        #设置UV的按钮ID
        self.buttonGroup_2.setId(self.UradioButton, 0)
        self.buttonGroup_2.setId(self.VradioButton, 1)
        self.setWindowTitle("FollicleTool_guyupi")


    def signalConnect(self):
        """
        设置相关按钮信号槽
        :return: None
        """
        self.createPlaneBt.clicked.connect(self.createPlane)
        self.createFollicleBt.clicked.connect(self.createFollicle)
        self.fromSpaceCreateBt.clicked.connect(self.fromobjCreate)
        self.maodingBt.clicked.connect(self.maoding)
        self.pushButton.clicked.connect(self.txtChange)

    @undoChunk_wrapper
    def createPlane(self):
        # 获取创建简模所需要的参数，法线方向，宽度，骨骼
        buttonId = self.buttonGroup.checkedId()
        jointList = cmds.ls(sl = 1)
        meshWidth = self.widthSpinBox.value()
        smooth = self.smoothCB.isChecked()
        headOffect = self.extrusionCB.isChecked()
        mesh.buid_meshJM(jointList ,meshWidth, buttonId ,headOffect ,smooth)

    @undoChunk_wrapper
    def createFollicle(self):
        #根据UV对模型创建毛囊
        buttonId = self.buttonGroup_2.checkedId()
        objList = cmds.ls(sl = 1)
        follicleNum = self.follicleSpinBox.value()

        ValuID = ["U","V"]

        fo1 = follicleUtils.Follicle()
        fo1.createFollicleForUV(ValuID[buttonId],objList,follicleNum)

    @undoChunk_wrapper
    def fromobjCreate(self):
        #在加载的模型上，选中物体创建毛囊
        sel = cmds.ls(sl = 1)
        fo1 = follicleUtils.Follicle()
        text = self.lineEdit.text()
        fo1.fromObjCreateFollile(text,sel)

    @undoChunk_wrapper
    def maoding(self):
        sel = cmds.ls(sl=1)
        fo1 = follicleUtils.Follicle()
        fo1.maodingFunc(sel)


    def txtChange(self):
        sel = cmds.ls(sl = 1)[0]
        self.lineEdit.setText(sel)

def main():

    UI = FollicleTool()
    UI.show()
    return UI

if __name__ == '__main__':
    main()
