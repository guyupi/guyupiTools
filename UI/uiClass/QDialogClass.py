#!/usr/bin/python
# -*- coding:utf-8 -*-
from PySide2 import QtWidgets, QtCore
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance


class BaseDialog(QtWidgets.QDialog):
    """
    Maya简单信息弹窗类

    使用示例:
        # 方法1: 直接使用静态方法
        SimpleMessageBox.show("提示标题", "这是消息内容")

        # 方法2: 创建实例后显示
        msg = SimpleMessageBox("提示标题", "这是消息内容")
        msg.show()
    """

    def __init__(self, title="Message", message="", parent=None ):
        """
        初始化消息窗口

        参数:
            title: 窗口标题
            message: 要显示的消息内容
            parent: 父窗口(自动获取Maya主窗口)
        """
        if parent is None:
            parent = self.get_maya_window()
        super(BaseDialog, self).__init__(parent)

        #设置窗口的内容
        self.resize(400, 300)
        self.setWindowTitle(title)

        Vertical_layout = QtWidgets.QVBoxLayout()
        leve_layout = QtWidgets.QHBoxLayout()
        #self.label = QtWidgets.QLabel(message)
        self.button_Confirm = QtWidgets.QPushButton(u"确认")
        self.button_Exit = QtWidgets.QPushButton(u"退出")

        #Vertical_layout.addWidget(self.label)
        leve_layout.addWidget(self.button_Confirm)
        leve_layout.addWidget(self.button_Exit)

        self.button_Confirm.clicked.connect(self.close)
        self.button_Exit.clicked.connect(self.close)
        self.show()
        self.exec_()

    def get_maya_window(self):
        """获取Maya主窗口"""
        maya_main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(long(maya_main_window_ptr), QtWidgets.QWidget)


