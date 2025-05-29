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

import uiDesigner.BlendShapeUI as UI
from ..utils.common import blendShapeTool
from ..utils.rigging import BlendShapeUtile
import uiClass.ListVisw as ListVisw

reload(ListVisw)
reload(BlendShapeUtile)
reload(UI)
reload(blendShapeTool)

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)  # 获得Maya主窗口


def undoChunk_wrapper(fn):  # wrapper 装饰器的名字，fn被装饰的函数（形参）
    # inner：被返回的函数，用来代替原函数
    def inner(*args, **kwargs):  # *args，**kwargs给原函数同样的参数配置
        """植入你想在执行目标函数之前要做的事情"""
        cmds.undoInfo(openChunk=True)
        try:
            ret = fn(*args, **kwargs)  # fn()是运行原函数，ret是原函数的返回值
        finally:
            pass

        cmds.undoInfo(closeChunk=True)
        return ret  # 将原函数的运行结果返回给调用方，在调用方看来，得到的结果韩式原函数的结果

    return inner  # 用来代替原函数


class BlendShapeTool(QWidget, UI.Ui_BlendShapeTool):  # 继承编译好的.py类

    def __init__(self, *args, **kwargs):
        super(BlendShapeTool, self).__init__(*args, **kwargs)

        # copy bs class
        self.copyBSTool = None
        self.EditeBlend = None
        self.setupUi(self)  # 运行父类初始化方法
        try:
            cmds.deleteUI('BlendShape_Tool')
        except RuntimeError:
            pass
        self.copy_connectAttr = None
        self.setObjectName("BlendShape_Tool")
        self.setParent(mayaMainWindow)  # 将新窗口设置为maya的子级
        self.setWindowFlags(Qt.Window)
        self.setWindow()

    def setWindow(self):
        self.setConnect()  # 设置链接槽函数
        self.loadMirrorModelBt.setDisabled(True)
        self.mirrorModelLe.setDisabled(True)


    def setConnect(self):
        # load BT
        self.loadSourceModelBt.clicked.connect(self.loadSourceMode_f)
        self.loadTargetModelBt.clicked.connect(self.loadTargetModel_f)
        self.loadMirrorModelBt.clicked.connect(self.loadMirrorModel_f)
        self.load_EditeModeBt.clicked.connect(self.load_EditeMode_fun)
        self.exitEditeBt.clicked.connect(self.exitEdite_fun)

        self.CreateBsBt.clicked.connect(self.createBs_funtion)
        self.checkMirrorBox.clicked.connect(self.checkMirror_f)
        self.createMediumBt.clicked.connect(self.createMedium)
        self.createWrapBt.clicked.connect(self.createWrap)
        self.tranBsBt.clicked.connect(self.tranBs_f)
        self.copyConnectBt.clicked.connect(self.copyConnect_f)
        self.pasteConnectBt.clicked.connect(self.pasteConnect_f)


    # load BT
    def loadSourceMode_f(self):
        sel = cmds.ls(sl=1)[0]
        if sel:
            self.sourceModelLe.setText(sel)

    def loadTargetModel_f(self):
        sel = cmds.ls(sl=1)[0]
        if sel:
            self.targetModelLe.setText(sel)

    def loadMirrorModel_f(self):
        sel = cmds.ls(sl=1)[0]
        if sel:
            self.mirrorModelLe.setText(sel)

    def load_EditeMode_fun(self):
        sel = cmds.ls(sl=1)[0]
        if sel:
            self.mirrorModelLe.setText(sel)
            self.EditeBlend = ListVisw.blendShape_ListWidget(sel)
            self.TargetQVL.addWidget(self.EditeBlend)
            self.loadModeLe.setText(sel)
        self.load_EditeModeBt.setDisabled(True)
        self.loadModeLe.setDisabled(True)

    def exitEdite_fun(self):
        self.TargetQVL.removeWidget(self.EditeBlend)
        self.EditeBlend.deleteLater()
        self.load_EditeModeBt.setDisabled(False)
        self.loadModeLe.setDisabled(False)


    def checkMirror_f(self):
        state = self.checkMirrorBox.isChecked()

        self.targetModelLe.setDisabled(state)
        self.loadTargetModelBt.setDisabled(state)
        if state:
            self.createMediumBt.setText(u"镜像介质")
            self.createWrapBt.setText(u"镜像包裹")
            self.tranBsBt.setText(u"提取形态")
        else:
            self.createMediumBt.setText(u"介质")
            self.createWrapBt.setText(u"包裹")
            self.tranBsBt.setText(u"传递")
        state = not state
        self.mirrorModelLe.setDisabled(state)
        self.loadMirrorModelBt.setDisabled(state)

    @undoChunk_wrapper
    def createBs_funtion(self):
        sel = cmds.ls(sl=1)
        if len(sel) < 2:
            return

        base_mode = sel[-1]
        mode_bs = BlendShapeUtile.BlendShapeClass(base_mode)
        for target in sel[:-1]:
            mode_bs.add_Target(target)

    @undoChunk_wrapper
    def createMedium(self):
        mirror = self.checkMirrorBox.isChecked()
        base_mode = self.sourceModelLe.text()
        target_mode = self.targetModelLe.text()
        mirror_mode = self.mirrorModelLe.text()
        print mirror, base_mode, target_mode, mirror_mode
        self.copyBSTool = blendShapeTool.CopyBlendShapeTool(base_mode, target_mode, mirror_mode)
        if mirror:
            if not base_mode and not mirror_mode:
                cmds.error(u"Please check the source model, the mirror model cannot be empty")
            elif not cmds.objExists(base_mode) and not cmds.objExists(mirror_mode):
                cmds.error(u"Please check if the source model and mirror model exist!")
            else:
                self.copyBSTool.create_mirrorMidMode()

        else:
            if not base_mode and not target_mode:
                cmds.error(u"请检查源模型,目标模型不能为空！！")
            elif not cmds.objExists(base_mode) and not cmds.objExists(target_mode):
                cmds.error(u"请检查源模型,目标模型是否存在！！")

            else:
                self.copyBSTool.create_MidMode()

    @undoChunk_wrapper
    def createWrap(self):

        exclusiveBind = self.exclusiveBindRbt.isChecked()
        deltaMush = self.deltaMushRbt.isChecked()
        mirror = self.checkMirrorBox.isChecked()

        self.copyBSTool.create_Warp(exclusiveBind=exclusiveBind, deltaMush=deltaMush, mirror=mirror)

    @undoChunk_wrapper
    def tranBs_f(self):
        mirror = self.checkMirrorBox.isChecked()
        lock = self.skipLockRbt.isChecked()
        lock = not lock
        self.copyBSTool.transfer_bs(unlock=lock, mirror=mirror)

    @undoChunk_wrapper
    def copyConnect_f(self):
        sel = cmds.ls(sl=1)[0]
        blendShapeClass = BlendShapeUtile.BlendShapeClass(sel)
        self.copy_connectAttr = blendShapeClass.copy_connectAttr()

    @undoChunk_wrapper
    def pasteConnect_f(self):
        sel = cmds.ls(sl=1)[0]
        blendShapeClass = BlendShapeUtile.BlendShapeClass(sel)
        blendShapeClass.paste_connectAttr(sel, self.copy_connectAttr)


def show():
    ui = BlendShapeTool()
    ui.show()
    return ui


if __name__ == '__main__':
    show()
