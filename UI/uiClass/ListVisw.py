#!/usr/bin/python
# -*- coding:utf-8 -*-
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from ...utils.rigging import BlendShapeUtile
import maya.cmds as cmds
from ...utils.rigging import arcUtils
reload(BlendShapeUtile)
reload(arcUtils)


class ListWidgetHelper:
    """不继承的增强工具类（推荐现代项目使用）"""

    @staticmethod
    def bind_count_changed(list_widget, callback):
        def emit_count():
            callback(list_widget.count())

        list_widget.model().rowsInserted.connect(emit_count)
        list_widget.model().rowsRemoved.connect(emit_count)
        return emit_count  # 返回断开连接的引用

class MyListWidget(QListWidget , arcUtils.baseFunTool):

    def __init__(self , *args):

        self.type = args
        super(MyListWidget, self).__init__()
        self.list_widget = CountAwareListWidget()
        self.list_widget.countChanged.connect(self.on_count_changed)

        # 设置相关属性
        self.setViewMode(QListView.ListMode)  # 设置列表形式显示
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置单选
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 设置多选
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置选择整行
        # self.setSortingEnabled(True)    #启用排列

        # 信号与槽
        self.doubleClicked.connect(self.item_double_clicked)  # 双击事件链接
        self.clicked.connect(self.item_clicked)

        # 右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.custom_right_menu)

    def item_clicked(self):
        selectList = self.currentItem()

    def item_double_clicked(self):
        # 获取选中的QListWidgetItem类，选中的文本
        pass

    def custom_right_menu(self, pos):
        menu = QMenu()
        opt1 = menu.addAction("新增")
        opt2 = menu.addAction("删除")
        opt3 = menu.addAction("排序")
        opt4 = menu.addAction("清空")
        clicked = menu.exec_(self.mapToGlobal(pos))
        if clicked == opt1:
            self.add_SelectMesh()
        elif clicked == opt2:
            self.delete_SelectItem()
        elif clicked == opt3:
            self.sort_List()
        elif clicked == opt4:
            self.clear_List()

    def add_SelectMesh(self):
        obj_select_list = cmds.ls(sl = 1 ,fl = 1)
        obj_select_dic = self.select_list_to_dic(obj_select_list)
        for key , value in obj_select_dic.items():
            obj_type = self.check_objType(key)
            #筛选出复合列表类型的东西
            if obj_type in self.type:
                self.addItem("{}:{}".format(key, value))

    def delete_SelectItem(self):
        selected_items = self.selectedItems()
        for item in selected_items:
            self.takeItem(self.row(item))

    def sort_List(self):
        self.sortItems()

    def clear_List(self):
        self.clear()

    def get_Text(self, text):
        strText = str(text)

    def update_TargetList(self):
        pass

    def on_count_changed(self):
        return self.count()
class blendShape_ListWidget(MyListWidget):

    def __init__(self, modeName):
        super(blendShape_ListWidget, self).__init__()
        self.blendShapeTool = BlendShapeUtile.BlendShapeClass(modeName)
        self.update_TargetList()

    def item_clicked(self):
        selected_items = self.currentItem()
        print selected_items.text()

    def item_double_clicked(self):
        selected_items = self.selectedItems()
        self.editItem(selected_items)
        pass

    def custom_right_menu(self, pos):
        menu = QMenu()
        opt1 = menu.addAction("新增")
        opt2 = menu.addAction("删除")
        opt3 = menu.addAction("反转")
        opt4 = menu.addAction("镜像")
        clicked = menu.exec_(self.mapToGlobal(pos))

        if clicked == opt1:
            self.add_SelectMesh()
        elif clicked == opt2:
            self.delete_SelectItem()
        elif clicked == opt3:
            self.flip_itemTarget()
        elif clicked == opt4:
            self.mirror_itemTarget()

    def add_SelectMesh(self):
        target_len = self.count()
        # print target_len
        cmds.blendShape(self.blendShapeTool.BlendShapeNode, edit=True,
                        target=(self.blendShapeTool.mode, target_len, "target_" + target_len, 1.0))

    def flip_itemTarget(self):
        selected_items = self.selectedItems()

        for item in selected_items:
            index = self.indexFromItem(item).row()
            self.blendShapeTool.flip_target(index)

    def mirror_itemTarget(self):
        selected_items = self.selectedItems()

        for item in selected_items:
            index = self.indexFromItem(item).row()
            self.blendShapeTool.mirror_target(index)

    def update_TargetList(self):
        for target in self.blendShapeTool.target:
            self.addItem(target)

    def clearList(self):
        pass
