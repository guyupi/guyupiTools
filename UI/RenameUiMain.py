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
import uiDesigner.nameUI as UI
from ..utils.rigging import nameUtils
reload(nameUtils)
reload(UI)


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
class ReNameUI(QWidget ,UI.Ui_RenameTool):  # 继承编译好的.py类

    def __init__(self, *args, **kwargs):
        super(ReNameUI, self).__init__(*args, **kwargs)
        self.setupUi(self)  # 运行父类初始化方法

        try:
            cmds.deleteUI('ReNameUI')
        except RuntimeError:
            pass


        self.copy_connectAttr = None
        self.setObjectName("ReNameUI")
        self.setParent(mayaMainWindow)  # 将新窗口设置为maya的子级
        self.setWindowFlags(Qt.Window)
        self.setWindow()



    #初始设置窗口的参数
    def setWindow(self):
        self.setConnect()  # 设置链接槽函数
        self.buttonGroup_nameType.setId(self.selectRB , 0)
        self.buttonGroup_nameType.setId(self.hierarchyRB, 1)
        self.buttonGroup_nameType.setId(self.allRb, 2)

    #设置窗口的
    def setConnect(self):
        self.RenamePB.clicked.connect(self.Rename)
        self.replacePB.clicked.connect(self.replace)
        self.add_pre_suffixPB.clicked.connect(self.add_pre_suffix)
        self.remove_pre_suffixPB.clicked.connect(self.remove_pre_suffix)
        self.check_duplicteNamePB.clicked.connect(self.check_duplicteName)
        self.remove_nameSpaceBT.clicked.connect(self.remove_nameSpace)

    def get_range(self):
        range = self.buttonGroup_nameType.checkedId()
        if range == 0:
            objList = cmds.ls(sl=1)
        elif range == 1:
            objList = cmds.ls(sl=1, dag=1)
        else:
            objList = cmds.ls(assemblies=True ,dag = 1)

        return objList

    @undoChunk_wrapper
    def Rename(self):

        objList = self.get_range()
        string = self.RenameLE.text()
        nameUtils.Name.batch_Rename(objList, string)
    @undoChunk_wrapper
    def replace(self):
        objList = self.get_range()
        old_string = self.OldStringLE.text()
        New_string = self.NewStringLE.text()
        nameUtils.Name.Replace_name(objList ,old_string , New_string)

    @undoChunk_wrapper
    def add_pre_suffix(self):
        objList = self.get_range()
        old_string = self.prefixLE.text()
        New_string = self.SuffixLE.text()
        nameUtils.Name.edit_prefix_suffix(objList, pre=old_string, suffix=New_string, edit_type=True)

    @undoChunk_wrapper
    def remove_pre_suffix(self):
        objList = self.get_range()
        old_string = self.prefixLE.text()
        New_string = self.SuffixLE.text()
        nameUtils.Name.edit_prefix_suffix(objList, pre=old_string, suffix=New_string, edit_type=False)

    def check_duplicteName(self):
        nameList = nameUtils.Name.check_duplicate_names()
        cmds.select(nameList)


    def remove_nameSpace(self):
        pass
def show():
    ui = ReNameUI()
    ui.show()
    return ui


if __name__ == '__main__':
    show()
