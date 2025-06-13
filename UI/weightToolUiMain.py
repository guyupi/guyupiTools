#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import uiClass.progressBar as proWin
import uiDesigner.weightTool as ui
from ..utils.rigging import skinUtils as skin
from ..utils.rigging import arcUtils as arc
import uiClass.ListVisw as lv
from ..utils.rigging import meshUtils as mesh
from ..utils.rigging import skinWeightUtils as skinToolUtils
import uiClass.WinSaveSetting as WinSaveSetting
reload(WinSaveSetting)
reload(mesh)
reload(skin)
reload(arc)
reload(lv)
reload(ui)
reload(proWin)

def undoChunk_wrapper(fn):    #wrapper 装饰器的名字，fn被装饰的函数（形参）
    #inner：被返回的函数，用来代替原函数
    def inner(*args,**kwargs):    #*args，**kwargs给原函数同样的参数配置
        """植入你想在执行目标函数之前要做的事情"""
        cmds.undoInfo(openChunk=True)
        ret = fn(*args,**kwargs)    #fn()是运行原函数，ret是原函数的返回值
        u"""植入你想在执行目标函数之后要做的事情"""
        cmds.undoInfo(closeChunk=True)
        return ret    #将原函数的运行结果返回给调用方，在调用方看来，得到的结果韩式原函数的结果
    return inner    #用来代替原函数

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)  # 获得Maya主窗口

#主页面功能UI
class SkinWeightUI(QWidget, ui.Ui_weigthTool ):  # 继承编译好的.py类
    def __init__(self, *args, **kwargs):
        # type: (object, object) -> object
        super(SkinWeightUI, self).__init__(*args, **kwargs)
        try:
            cmds.deleteUI('weigthTool')
        except RuntimeError:
            pass
        self.setObjectName("weigthTool")

        self.settings = WinSaveSetting.PluginSettingsManager("weigthTool")

        self.setParent(mayaMainWindow)  # 将新窗口设置为maya的子级
        self.setWindowFlags(Qt.Window)
        self.setupUi(self)  # 运行父类初始化方法+


        self.setConnect()   #设置链接槽函数
        self.setWindow()  # 设置窗口的相关参数
        self.load_settings()

    def setWindow(self):
        self.setListVisw()
        self.set_icon()
        #设置buttonGroup的按钮ID
        self.buttonGroup.setId(self.moreToMore_radioButton,0)
        self.buttonGroup.setId(self.moreToOne_radioButton,1)
        self.buttonGroup.setId(self.oneToMore_radioButton,2)

        self.listNumLabel()

    def save_settings(self):
        # 保存UI状态
        self.settings.save_ui_settings(self)

    def load_settings(self):
        # 加载UI状态
        self.settings.load_ui_settings(self)

    def closeEvent(self, event):
        # 窗口关闭时自动保存设置
        self.save_settings()
        super(QWidget, self).closeEvent(event)

    def listNumLabel(self):
        # countA = self.left_listWidget.count()

        # self.left_ListNu_Label.setText(str(countA))
        # countB = self.right_listWidget.count()
        # self.right_ListNu_Label.setText(str(countB))
        left_widgt_count_tool = lv.ListWidgetHelper()
        left_widgt_count_tool.bind_count_changed(self.left_listWidget, lambda num: self.left_ListNu_Label.setText(str(num)))
        right_widgt_count_tool = lv.ListWidgetHelper()
        right_widgt_count_tool.bind_count_changed(self.right_listWidget, lambda num: self.right_ListNu_Label.setText(str(num)))


    def setConnect(self):
        #Button clicked
        self.skin_Button.clicked.connect(self.bindSkin)
        self.copy_Skin_oneTomore_Button.clicked.connect(self.copy_Skin_oneTomore)
        self.copy_Skin_moreToone_Button.clicked.connect(self.copy_Skin_moreToone)
        self.add_inf_Button.clicked.connect(self.addInfJoints)
        self.weightRelax_Button.clicked.connect(self.weightRelax)
        self.remove_inf_button.clicked.connect(self.reomveZeroWeiJoint)
        self.clear_wei_Button.clicked.connect(self.clearSmellWei)
        self.find_four_wei_Button.clicked.connect(self.checkFourWei)
        self.remove_fourwei_Button.clicked.connect(self.removePointWei)
        self.import_skinWei_Button.clicked.connect(self.importSkinWei)
        self.export_skinWei_Button.clicked.connect(self.exportSkinWei)
        self.copyPointWeiButton.clicked.connect(self.copyPointWei)
        self.patePointSkinWeiButton.clicked.connect(self.patePointSkinWei)
        self.MirrorWeightButton01.clicked.connect(self.MirrorWeight)
        self.MirrorWeightButton01_2.clicked.connect(self.MirrorWeightRev)
        self.hammer_wei_button.clicked.connect(self.hammer_wei)
        self.copySkinWeiButton.clicked.connect(self.copySkinWeight)
        self.resetSkinNodeBt.clicked.connect(self.resetSkinNode)
        self.clear_ObjList_Button.clicked.connect(self.clear_ViewObjList)
    #设置按钮图标
    def set_icon(self):

        self.skin_Button.setIcon(QIcon(":smoothSkin.png"))
        self.remove_inf_button.setIcon(QIcon("removeWrapInfluence.png"))
        self.add_inf_Button.setIcon(QIcon("addWrapInfluence.png"))

    def clear_ViewObjList(self):
        self.left_listWidget.clear()
        self.right_listWidget.clear()

    #listVisw列表设置
    def setListVisw(self):
        lift_type = "mesh"
        right_type = "mesh" ,"nurbsSurface" , "nurbsCurve"
        self.left_listWidget = lv.MyListWidget(lift_type)
        self.right_listWidget = lv.MyListWidget(*right_type)
        self.horizontalLayout_8.addWidget(self.left_listWidget)
        self.horizontalLayout_8.addWidget(self.right_listWidget)


    def addRightVisw_mode(self):
        allObj = cmds.ls(sl=1)
        filter = arc.Filter()
        mesh = filter.GetFilter(allObj,"mesh",False)
        self.left_listWidget.addItem("add")
        self.left_listWidget.addItem("add")

    @undoChunk_wrapper
    def MirrorWeight(self):
        str = " -mirrorMode YZ -surfaceAssociation closestPoint -influenceAssociation oneToOne -influenceAssociation closestJoint"
        mel.eval("doMirrorSkinWeightsArgList( 2, { \" " + str + " \" } );")

    @undoChunk_wrapper
    def MirrorWeightRev(self):
        str = " -mirrorMode YZ -mirrorInverse -surfaceAssociation closestPoint -influenceAssociation oneToOne -influenceAssociation closestJoint"
        mel.eval("doMirrorSkinWeightsArgList( 2, { \" " + str + " \" } );")

    @undoChunk_wrapper
    def bindSkin(self):

        with arc.GetFilter('mesh') as Get:
            mesh = Get.filterObjs
        with arc.GetFilter('joint') as Get:
            joint = Get.filterObjs
        print mesh , joint
        skinToolUtils.skinTool.build_bind(mesh , joint)

    @undoChunk_wrapper
    def weightRelax(self):
        stepNum = self.stepsNumspinBox.value()
        stepsSize = self.stepsSizeSpinBox.value()
        objects = cmds.ls(sl=True) + cmds.ls(hl=True)
        skin.relax_pointWeight(objects , stepNum ,stepsSize )

    @undoChunk_wrapper
    def copy_Skin_moreToone(self):

        objList = cmds.ls(sl=1)
        skinToolUtils.copySkinTool.CopySkin_MoreToOne(*objList)

    @undoChunk_wrapper
    def copy_Skin_oneTomore(self):
        mesh = cmds.ls(sl = 1)
        skin_node = skinToolUtils.skinTool.get_SkinNode(mesh[0])
        if skin_node:
            for obj  in mesh[1:]:
                skinToolUtils.copySkinTool.CopySkin_OneToOne(mesh[0] , [obj])

    @undoChunk_wrapper
    def copyPointWei(self):
        mel.eval("artAttrSkinWeightCopy")

    @undoChunk_wrapper
    def patePointSkinWei(self):
        mel.eval("artAttrSkinWeightPaste")

    @undoChunk_wrapper
    def copySkinWeight(self):
        coptype = self.buttonGroup.checkedId()
        left_list = self.left_listWidget.count()
        right_list = self.right_listWidget.count()
        if coptype == 0:
            for num in range(min(left_list,right_list)):
                #获取文本，并复制,获取的文本信息为字符串，在使用时需要将字符串转化为列表
                pointList = self.left_listWidget.item(num).text().split("->")
                if pm.mel.findRelatedSkinCluster(pointList[0]):
                    left_mesh = mesh.meshTool.copyMesh(eval(pointList[1]))
                    #print pointList[0], left_mesh
                    skin.CopySkin_OneToOne(pointList[0],left_mesh)

                    right_text = self.right_listWidget.item(num).text().split("->")
                    skin.CopySkin_OneToOne(left_mesh[0],eval(right_text[1]))

                    cmds.delete(left_mesh)
                else:
                    cmds.error("object don`t have skinNode")
                    continue

        elif coptype == 1:
            #创建出左边模型的集合体
            tempmesh = []
            left_mesh = []
            for objnum in range(left_list):

                pointList = self.left_listWidget.item(objnum).text().split("->")

                if   pm.mel.findRelatedSkinCluster(pointList[0]) == "":
                    cmds.error("object don`t have skinNode")
                    cmds.delete(tempmesh)
                    return
                else:
                    left_temp_mesh = mesh.meshTool.copyMesh(eval(pointList[1]))[0]
                    tempmesh.append(left_temp_mesh)
                    left_mesh.append(pointList[0])

            combnemesh = mesh.meshTool.combneMesh(tempmesh)
            #获取所有左侧列表的所有影响骨骼骨骼并绑定蒙皮合并后的骨骼
            jointList = []
            for num in range(left_list):
                pointList = self.left_listWidget.item(num).text().split("->")
                ObjAInfJoint = pm.skinCluster(pointList[0], q=True, inf=True)
                jointList +=ObjAInfJoint
            jointList = list(set(jointList))

            pm.skinCluster(combnemesh, jointList, tsb=True)
            cmds.select(left_mesh, r= 1)
            cmds.select(combnemesh,add = 1)
            mel.eval("copySkinWeights  -noMirror -surfaceAssociation closestPoint -influenceAssociation closestJoint -influenceAssociation oneToOne;")
            #将权重一一拷贝给右侧列表
            for num in range(right_list):
                rightPoint = self.right_listWidget.item(num).text().split("->")
                skin.CopySkin_OneToOne(combnemesh[0],eval(rightPoint[1]))
            cmds.delete(combnemesh)
        elif coptype == 2:
            #复制左侧的模型
            leftpoint = self.left_listWidget.item(0).text().split("->")

            leftmesh = mesh.meshTool.copyMesh(eval(leftpoint[1]))
            skin.CopySkin_OneToOne(leftpoint[0],leftmesh)
            for obj in range(right_list):
                rightpoint = self.right_listWidget.item(obj).text().split("->")
                skin.CopySkin_OneToOne(leftmesh[0],eval(rightpoint[1]))
            cmds.delete(leftmesh)

    @undoChunk_wrapper
    def addInfJoints(self):
        with arc.GetFilter('mesh') as Get:
            mesh = Get.filterObjs
        with arc.GetFilter('joint') as Get:
            joint = Get.filterObjs
        for obj in mesh:
            skinToolUtils.skinTool.add_infJoint(obj ,joint)
        print(u'添加影响成功！')

    @undoChunk_wrapper
    def resetSkinNode(self):

        with arc.GetFilter('mesh') as Get:
            meshList = Get.filterObjs
        for mesh in meshList:
            skinToolUtils.skinTool.reset_skin_node(mesh)

    @undoChunk_wrapper
    def reomveZeroWeiJoint(self):
        mel.eval("removeUnusedInfluences")

    @undoChunk_wrapper
    def clearSmellWei(self):
        num = self.doubleSpinBox.value()
        with arc.GetFilter('mesh') as Get:
            mesh_List = Get.filterObjs

        for mesh in mesh_List:
            skinToolUtils.skinTool.prune_small_weights(mesh ,num)
            skinToolUtils.skinTool.normalize_weights(mesh)

    @undoChunk_wrapper
    def checkFourWei(self):
        num = self.numWeispinBox.value()
        skin.buttonCommand_checkInflunce(num)
        print("检查超点权重！")

    @undoChunk_wrapper
    def removePointWei(self):
        num = self.numWeispinBox.value()
        skin.buttonCommand_forceClear(num)
        print("清理超点权重！")

    def exportSkinWei(self):
        with arc.GetFilter('mesh') as GetMesh:
            meshes = GetMesh.filterObjs
            if meshes:
                with proWin.ProgressWin(len(meshes), 'exporting weights: ') as pr:
                    for i, m in enumerate(meshes):

                        skins = arc.get_skinCluster(m)
                        if not skins:
                            cmds.warning('{} has no skinCluster'.format(m))
                            continue

                        skin.compose_weights_data(m)
                        pr.edit_window(i, text='exporting weights - {} - '.format(m))
        pass

    @undoChunk_wrapper
    def importSkinWei(self):
        with arc.GetFilter('mesh') as GetMesh:
            meshes = GetMesh.filterObjs
            if meshes:
                with proWin.ProgressWin(len(meshes), 'importing weights: ') as pr:
                    for i, m in enumerate(meshes):

                        skins = arc.get_skinCluster(m)
                        # if not skin:
                        #     cmds.warning('{} has no skinCluster'.format(m))
                        #     continue
                        data = skin.decompose_weights_data(m)
                        pr.edit_window(i, text='importing weights - {} - '.format(m))
        pass

    @undoChunk_wrapper
    def hammer_wei(self):
        sel = cmds.ls(sl = 1 ,fl =1 )
        skinToolUtils.skinTool.maya_hammer_wei()

def show():
    UI = SkinWeightUI()
    UI.show()
    return UI

if __name__ == '__main__':
    show()




