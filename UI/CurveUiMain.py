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

import uiDesigner.CurveUI as UI
from ..utils.rigging import control
from ..utils.rigging import curveUtile
reload(curveUtile)
reload(UI)
reload(control)

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



class ScaleList(QListWidget):

    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() != Qt.ControlModifier:
            QListWidget.wheelEvent(self, event)
        else:
            if event.delta() > 0:
                w = min(self.iconSize().width() + 4, 128)
                self.setIconSize(QSize(w, w))
                for i in range(self.count()):
                    self.item(i).setSizeHint(QSize(w+3, w+3))
            elif event.delta() < 0:
                w = max(self.iconSize().width() - 4, 16)
                self.setIconSize(QSize(w, w))
                for i in range(self.count()):
                    self.item(i).setSizeHint(QSize(w + 3, w + 3))


class ShapeList(ScaleList):

    def __init__(self):
        ScaleList .__init__(self)
        self.update_shapes()
        self.setMovement(self.Static)
        # self.setSelectionMode(self.ExtendedSelection)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewMode(self.IconMode)
        self.setIconSize(QSize(64, 64))
        self.setResizeMode(self.Adjust)
        self.itemDoubleClicked.connect(self.double_clicked)
        self.menu = QMenu(self)
        self.menu.addAction(u"upload", self.upload_control)
        self.menu.addAction(u"delete", self.delete_control)

    def contextMenuEvent(self, event):
        QListWidget.contextMenuEvent(self, event)
        self.menu.exec_(event.globalPos())


    def update_shapes(self):
        self.clear()
        #data_dir = os.path.abspath(__file__ + "/../data/")
        current_file_path = os.path.abspath(__file__ )
        parentA_dir = os.path.dirname(current_file_path )
        parentB_dir = os.path.dirname(parentA_dir)
        data_dir = os.path.join(parentB_dir, 'data')

        for file_name in os.listdir(data_dir):
            name, ext = os.path.splitext(file_name)
            if ext != ".jpg":
                continue
            jpg_file = os.path.join(data_dir, file_name)
            icon = QIcon(jpg_file)
            item = QListWidgetItem(icon, "", self)
            item.name = name
            item.setSizeHint(QSize(67, 67))

    @staticmethod
    def double_clicked(item):
        pm.undoInfo(openChunk=1)
        s = item.name

        selected =control.Control.selected()
        if selected:
            control.Control.set_selected(s=s, r=1)
        else:
            control.Control(n=s, s=s, r=1)
        pm.undoInfo(closeChunk=1)

    def upload_control(self):
        pm.undoInfo(openChunk=1)
        for con in control.Control.selected():
            con.upload()
        self.update_shapes()
        pm.undoInfo(closeChunk=1)

    def delete_control(self):
        pm.undoInfo(openChunk=1)
        shapes = [item.name for item in self.selectedItems()]
        control.Control.delete_shapes(*shapes)
        self.update_shapes()
        pm.undoInfo(closeChunk=1)




class CurveTool(QWidget, UI.Ui_CurveUI):  # 继承编译好的.py类

    def __init__(self, *args, **kwargs):
        # type: (object, object) -> object
        super(CurveTool, self).__init__(*args, **kwargs)
        self.setupUi(self)  # 运行父类初始化方法
        try:
            cmds.deleteUI('curveTool')
        except RuntimeError:
            pass
        self.setObjectName("curveTool")

        self.setParent(mayaMainWindow)  # 将新窗口设置为maya的子级
        self.setWindowFlags(Qt.Window)

        self.setWindow()



    def setWindow(self):

        self.setConnect()  # 设置链接槽函数
        self.setColorList()
        shapeList = ShapeList()
        self.verticalLayout_5.addWidget(shapeList)
        self.yueshuRadBt.setChecked(True)
        self.buttonGroup.setId(self.yueshuRadBt,0)
        self.buttonGroup.setId(self.fuziRadBt, 1)
        self.buttonGroup.setId(self.lianjieRadBt ,2)
        self.ContorlTool.setCurrentIndex(0)

    def setConnect(self):
        self.CurveScaleBt.clicked.connect(self.setCurveScale)
        self.loadCurveBt.clicked.connect(self.loadCurve)
        self.replaceCurveBt.clicked.connect(self.replaceCurve)
        self.IkBt.clicked.connect(self.CreateIK)
        self.FKbt.clicked.connect(self.CreateFK)
        self.IKFKBt.clicked.connect(self.CreateIKFK)
        self.FKcijiBt.clicked.connect(self.CreateFKciji)
        self.loadCurveBt02.clicked.connect(self.loadCurveB)
        self.extracCurvetBt.clicked.connect(self.extracCurve)
        self.create_curveLocBT.clicked.connect(self.create_curveLoc)


    def setColorList(self):
        index_rgb_map = [
            # [0.5, 0.5, 0.5],
            # [0, 0, 0],
            # [0.247, 0.247, 0.247],
            # [0.498, 0.498, 0.498],
            [0.608, 0, 0.157],
            [0, 0.16, 0.376],
            [0, 0, 1],
            [0, 0.275, 0.094],
            [0.149, 0, 0.263],
            [0.78, 0, 0.78],
            [0.537, 0.278, 0.2],
            [0.243, 0.133, 0.121],
            [0.6, 0.145, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0.2549, 0.6],
            [1, 1, 1],
            [1, 1, 0],
            [0.388, 0.863, 1],
            [0.263, 1, 0.639],
            [1, 0.686, 0.686],
            [0.89, 0.674, 0.474],
            [1, 1, 0.388],
            # [0, 0.6, 0.329],
            # [0.627, 0.411, 0.188],
            # [0.619, 0.627, 0.188],
            # [0.408, 0.631, 0.188],
            # [0.188, 0.631, 0.365],
            # [0.188, 0.627, 0.627],
            # [0.188, 0.403, 0.627],
            # [0.434, 0.188, 0.627],
            # [0.627, 0.188, 0.411],
        ]

        for i, rgb in enumerate(index_rgb_map):
            button = QPushButton()
            button.setFixedSize(15 ,40)
            self.horizontalLayout.addWidget(button)
            #button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            pix = QPixmap(128, 128)
            pix = pix.scaled(15, 40)
            pix.fill(QColor.fromRgbF(*rgb))
            button.setIcon(QIcon(pix))
            button.setIconSize(QSize(15,40))

            button.clicked.connect(lambda checked = False, idx=(i + 4): self.setColor(idx))

    def setColor(self,col):
        sel = cmds.ls(sl = 1)
        for a in sel:
            shape = cmds.listRelatives(a, s=1)[0]
            cmds.setAttr(shape + ".overrideEnabled", 1)
            cmds.setAttr(shape + ".overrideColor", col)


    @undoChunk_wrapper
    def setCurveScale(self):
        ScaleNum = self.CurveScaleNum.value()
        control.Control.set_selected(r=ScaleNum)

    def loadCurve(self):
        sel = cmds.ls(sl = 1)[0]
        self.CurveName.setText(sel)

    def loadCurveB(self):
        sel = cmds.ls(sl=1)
        self.CurveSelectLE.setText(str(sel))


    def get_dirveType(self):
        ID = self.buttonGroup.checkedId()
        if ID == 0:
            return "yueshu"
        elif ID == 1:
            return  "fuzi"
        elif ID == 2:
            return  "lianjie"

    @undoChunk_wrapper
    def replaceCurve(self):
        selected = control.Control.name_select(self.CurveName.text())
        target = control.Control.selected()

        shape = selected[0].get_shape()

        for con in target:
            con.set_shape(shape)

    @undoChunk_wrapper
    def mirror_control(self):
        control.Control.mirror_selected()

    @undoChunk_wrapper
    def CreateIK(self):
        sel = cmds.ls(sl = 1 )
        if not sel:
            cmds.warning("nothing select!")
            return
        dirveType = self.get_dirveType()
        control.ControlClass.createAloneCon(objList = sel  ,cvShape = "cube" ,dirveType=dirveType )


    @undoChunk_wrapper
    def CreateFK(self):
        sel = cmds.ls(sl=1 , dag = 1)
        if not sel:
            cmds.warning("nothing select!")
            return
        dirveType = self.get_dirveType()
        endCon = self.EndRadBt.isChecked()
        control.ControlClass.createFKCon(objList=sel, cvShape="PlaneD" , endCon = endCon ,dirveType=dirveType )

    @undoChunk_wrapper
    def CreateIKFK(self):
        sel = cmds.ls(sl=1, dag=1)
        if not sel:
            cmds.warning("nothing select!")
            return
        dirveType = self.get_dirveType()
        endCon = self.EndRadBt.isChecked()
        control.ControlClass.createFKIKCon(objList=sel, cvShape="PlaneD",IKciji= True ,endCon = endCon ,dirveType=dirveType )

    @undoChunk_wrapper
    def CreateFKciji(self):
        sel = cmds.ls(sl=1, dag=1)
        if not sel:
            cmds.warning("nothing select!")
            return
        ctrl_list = control.ControlClass.createFKIKCon(objList=sel, cvShape="PlaneD", endCon=False, IKciji=True)
        # print ctrl_list
        control.ControlClass.FkCiJi(ctrl_list )

    @undoChunk_wrapper
    def extracCurve(self):
        curve = self.CurveSelectLE.text()
        sel = cmds.ls(sl = 1)
        control.ControlClass.extractCurve(eval(curve) , sel)

    @undoChunk_wrapper
    def create_curveLoc(self):
        curveList = cmds.ls(sl = 1)
        curveUtile.curveTool.createLocForCurve(curveList)

def show():
    ui = CurveTool()
    ui.show()
    return ui

if __name__ == '__main__':
    show()








