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
import uiDesigner.jointToolUi as jointUI
from ..utils.rigging import jointUtils
from ..utils.rigging import commonsUtile
reload(jointUtils)
reload(jointUI)


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
class JointTool(QWidget ,jointUI.Ui_JointTool):  # 继承编译好的.py类

    def __init__(self, *args, **kwargs):
        super(JointTool, self).__init__(*args, **kwargs)
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
        self.buttonGroup_Orientation.setId(self.XYRB , 0)
        self.buttonGroup_Orientation.setId(self.YZRB, 1)
        self.buttonGroup_Orientation.setId(self.XZRB, 2)

        self.buttonGroup_Type.setId(self.BehaviorRB, 1)
        self.buttonGroup_Type.setId(self.OrientationRB, 0)


    #设置窗口的
    def setConnect(self):
        self.batchCreateJointsBt.clicked.connect(self.batchCreateJoints)
        self.CreateOneJointsBt.clicked.connect(self.CreateOneJoints)
        self.cvToJointBt.clicked.connect(self.cvToJoint)
        self.insertJointBt.clicked.connect(self.insertJoint)
        self.mirrorJointBT.clicked.connect(self.mirrorJoint)
        self.splitJointBt.clicked.connect(self.splitJoint)
        self.combineJointBt.clicked.connect(self.combineJoint)

        self.switchDirectionBt.clicked.connect(self.switchDirection)
        self.selectHisJointsBt.clicked.connect(self.selectHisJoints)
        self.selectSkinJointsBt.clicked.connect(self.selectSkinJoints)
        self.jointSizeQS.valueChanged.connect(self.changejointSize)
        self.makeIdentityBt.clicked.connect(self.makeIdentityFun)

    @undoChunk_wrapper
    def batchCreateJoints(self):

        skin = self.andBiendSkin.isChecked()
        sel = cmds.ls(sl = 1)
        jointUtils.jointCla.createJointsForPoly(sel ,skin)


    @undoChunk_wrapper
    def CreateOneJoints(self):
        skin = self.andBiendSkin.isChecked()
        sel = cmds.ls(sl=1)
        jointUtils.jointCla.createJointForPoly(sel ,skin)

    @undoChunk_wrapper
    def cvToJoint(self):
        distance = self.distanceCB.isChecked()
        jointNum = self.CvToJointsNum.value()
        # print distance , jointNum
        curve = cmds.ls(sl=1)

        jointUtils.jointCla.create_curveToJoint(curve , jointNum, equidistance=distance)

    @undoChunk_wrapper
    def insertJoint(self):

        jointNum = self.insertJointNum.value()

        jointList = cmds.ls(sl=1 ,type = 'joint')

        jointUtils.jointCla.create_MidJoint(jointList, jointNum)

    @undoChunk_wrapper
    def mirrorJoint(self):
        jointList = cmds.ls(sl=1 ,type = 'joint')

        leve = self.buttonGroup_Orientation.checkedId()
        type = self.buttonGroup_Type.checkedId()

        old_string = self.mirrorOldStringLE.text()
        new_string = self.mirrorNewStringLE.text()
        jointUtils.jointCla.Batch_mirrorJoint( jointList,  leve , type , old_string ,new_string )

    @undoChunk_wrapper
    def splitJoint(self):
        jointList = cmds.ls(sl=1, type='joint')
        size = commonsUtile.get_sceneSizeforMesh()
        jointUtils.jointCla.create_loc(jointList , size)


    @undoChunk_wrapper
    def combineJoint(self):
        jointUtils.jointCla.change_jointRotate()

    @undoChunk_wrapper
    def switchDirection(self):
        jointUtils.jointCla.dis_rotation()

    @undoChunk_wrapper
    def selectHisJoints(self):
        sel = cmds.ls(sl=1)
        jointUtils.jointCla.select_hisJoint(sel)

    @undoChunk_wrapper
    def selectSkinJoints(self):
        sel = cmds.ls(sl = 1)
        jointUtils.jointCla.select_skin_jointList(sel)



    @undoChunk_wrapper
    def makeIdentityFun(self):
        sel = cmds.ls(sl=1 , type= "joint")
        jointUtils.jointCla.makeIdentity_joint(sel)

    def changejointSize(self ,value):
        jointUtils.jointCla.change_jointSize(value *0.05)

def show():
    ui = JointTool()
    ui.show()
    return ui


if __name__ == '__main__':
    show()
