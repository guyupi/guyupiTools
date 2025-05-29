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
import uiDesigner.ConvertWeightUI as UI
from ..utils.common import ConverWeiTool
from ..utils.rigging import skinWeightUtils
reload(skinWeightUtils)
reload(ConverWeiTool)
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
class ConvertWeightUI(QWidget , UI.Ui_ConvertWeightTool):  # 继承编译好的.py类

    def __init__(self, *args, **kwargs):
        super(ConvertWeightUI, self).__init__(*args, **kwargs)
        self.setupUi(self)  # 运行父类初始化方法

        try:
            cmds.deleteUI('ConvertWeightToolUI')
        except RuntimeError:
            pass
        self.copy_connectAttr = None
        self.setObjectName("ConvertWeightToolUI")
        self.setParent(mayaMainWindow)  # 将新窗口设置为maya的子级
        self.setWindowFlags(Qt.Window)
        self.setWindow()

    #初始设置窗口的参数
    def setWindow(self):
        self.setConnect()  # 设置链接槽函数
        self.RootJointListLE_loadBt.setDisabled(True)
        self.RootJointListLE.setDisabled(True)
        self.buttonGroup_weightTtype.setId(self.oneByOneRB , 1)
        self.buttonGroup_weightTtype.setId(self.offsetOneRB, 2)
        self.buttonGroup_weightTtype.setId(self.offsetEndRB, 3)

        self.buttonGroup_curveType.setId(self.curveTypeARB ,1)
        self.buttonGroup_curveType.setId(self.curveTypeBRB, 2)
        self.buttonGroup_curveType.setId(self.curveTypeCRB, 3)
    #设置窗口的
    def setConnect(self):
        #loadBT
        self.meshLE_loadBt.clicked.connect(self.loadMesh)
        self.RootJointLE_loadBt.clicked.connect(self.loadRootJoint)
        self.ChildrenLe_loadBt.clicked.connect(self.loadChildren)
        self.RootJointListLE_loadBt.clicked.connect(self.loadRootJointList)

        #正常的按钮信号
        self.RootJointListCB.clicked.connect(self.checkRootJointList)
        self.ConvertWeightPB.clicked.connect(self.ConvertWeight)
        self.IntegratedWeightPB.clicked.connect(self.IntegratedWeight)

    def loadMesh(self):
        mesh = cmds.ls(sl = 1)[0]
        self.meshLE.setText(mesh)

    def loadRootJoint(self):
        RootJoint = cmds.ls(sl=1 ,type = "joint")[0]
        self.RootJointLE.setText(RootJoint)
        childrenJoint = cmds.ls(RootJoint , dag = 1 ,type = "joint")[1:]
        result = "; ".join(childrenJoint)
        self.ChildrenLe.setText(result)

    def loadChildren(self):
        Joints = cmds.ls(sl=1,type = "joint")
        result = "; ".join(Joints)
        self.ChildrenLe.setText(result)

    def loadRootJointList(self):
        RootJointList = cmds.ls(sl=1,type = "joint")
        result = "; ".join(RootJointList)
        self.RootJointListLE.setText(result)

    def checkRootJointList(self):
        if self.RootJointListCB.isChecked():
            self.RootJointLE.setDisabled(True)
            self.RootJointLE_loadBt.setDisabled(True)
            self.ChildrenLe.setDisabled(True)
            self.ChildrenLe_loadBt.setDisabled(True)
            self.RootJointListLE_loadBt.setDisabled(False)
            self.RootJointListLE.setDisabled(False)
        else:
            self.RootJointLE.setDisabled(False)
            self.RootJointLE_loadBt.setDisabled(False)
            self.ChildrenLe.setDisabled(False)
            self.ChildrenLe_loadBt.setDisabled(False)
            self.RootJointListLE_loadBt.setDisabled(True)
            self.RootJointListLE.setDisabled(True)

    @undoChunk_wrapper
    def ConvertWeight(self):
        mesh = self.meshLE.text()
        rootJoint = self.RootJointLE.text()
        sepJointList = self.ChildrenLe.text().split("; ")
        Type = self.buttonGroup_weightTtype.checkedId()
        Degree = self.buttonGroup_curveType.checkedId()
        Percent = self.percent_spinBox.value()

        #实例化工具
        tool =ConverWeiTool.ConvertWeiTool(mesh=mesh, rootJoint=rootJoint, sepJointList=sepJointList,Degree = Degree , Type=Type, Percent=Percent)

        #创建线包裹
        jointList = [rootJoint] + sepJointList
        curve = tool.create_CvByJoint(jointList)
        wirs_mesh = tool.copy_mesh(mesh)
        wirs = [curve, wirs_mesh]
        wire1 = tool.build_wire(wirs)[0]

        tool.transfer_jointZeroWeights(mesh, rootJoint, sepJointList)

        #对线包裹的曲线上的点，用变形器簇
        deform_list = tool.build_cluster(curve)

        #将骨骼root骨骼权重转移到线包裹的封套上
        vtx = cmds.ls("{}.vtx[*]".format(mesh), fl=1)
        vtxList = list(range(0, len(vtx)))

        mesh_skinNode = tool.get_SkinNode(mesh)
        inf_jointList = tool.get_infJointList(mesh_skinNode)
        inf_jointNum = []
        inf_jointNum.append(inf_jointList.index(rootJoint))

        weights = tool.get_apiMeshSkinWeight(mesh=mesh, inf=list(inf_jointNum))

        tool.move_jointWeightsToDeform(wire1, wirs_mesh, vtx, weights)

        allWeights = tool.get_apiMeshSkinWeight(mesh=mesh)
        for deform ,joint in zip(deform_list ,sepJointList):
            # 获取每个簇对应的权重数值，并分配给对应骨骼
            target_wei = tool.get_clusterWei(wirs_mesh, deform=deform)

            new_weights = tool.subtract_jointWeights(mesh, allWeights, rootJoint, joint, target_wei, Type="-")
            print deform ,joint
            allWeights = new_weights
        tool.set_apiMeshWeight(mesh=mesh, weights=allWeights)

        #删除过程垃圾
        cmds.delete(deform_list , wirs_mesh  ,curve)


    @undoChunk_wrapper
    def IntegratedWeight(self):
        mesh = self.meshLE.text()
        rootJoint = self.RootJointLE.text()
        sepJointList = self.ChildrenLe.text().split("; ")
        tool = skinWeightUtils.SkinWeight()
        # for joint in sepJointList:
        tool.transfer_jointZeroWeights(mesh , rootJoint ,sepJointList)


def show():
    ui = ConvertWeightUI()
    ui.show()
    return ui


if __name__ == '__main__':
    show()
