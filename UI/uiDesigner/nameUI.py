# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nameUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide2 import QtCore, QtGui, QtWidgets


class Ui_RenameTool(object):
    def setupUi(self, RenameTool):
        RenameTool.setObjectName("RenameTool")
        RenameTool.resize(382, 253)
        self.verticalLayout = QtWidgets.QVBoxLayout(RenameTool)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.RenameLE = QtWidgets.QLineEdit(RenameTool)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RenameLE.sizePolicy().hasHeightForWidth())
        self.RenameLE.setSizePolicy(sizePolicy)
        self.RenameLE.setObjectName("RenameLE")
        self.gridLayout.addWidget(self.RenameLE, 2, 1, 2, 1)
        self.prefixLE = QtWidgets.QLineEdit(RenameTool)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prefixLE.sizePolicy().hasHeightForWidth())
        self.prefixLE.setSizePolicy(sizePolicy)
        self.prefixLE.setObjectName("prefixLE")
        self.gridLayout.addWidget(self.prefixLE, 11, 1, 1, 1)
        self.line_2 = QtWidgets.QFrame(RenameTool)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 5, 0, 1, 3)
        self.add_pre_suffixPB = QtWidgets.QPushButton(RenameTool)
        self.add_pre_suffixPB.setObjectName("add_pre_suffixPB")
        self.gridLayout.addWidget(self.add_pre_suffixPB, 11, 2, 1, 1)
        self.remove_pre_suffixPB = QtWidgets.QPushButton(RenameTool)
        self.remove_pre_suffixPB.setObjectName("remove_pre_suffixPB")
        self.gridLayout.addWidget(self.remove_pre_suffixPB, 12, 2, 1, 1)
        self.check_duplicteNamePB = QtWidgets.QPushButton(RenameTool)
        self.check_duplicteNamePB.setObjectName("check_duplicteNamePB")
        self.gridLayout.addWidget(self.check_duplicteNamePB, 13, 0, 1, 3)
        self.label_5 = QtWidgets.QLabel(RenameTool)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 7, 0, 1, 1)
        self.replacePB = QtWidgets.QPushButton(RenameTool)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.replacePB.sizePolicy().hasHeightForWidth())
        self.replacePB.setSizePolicy(sizePolicy)
        self.replacePB.setObjectName("replacePB")
        self.gridLayout.addWidget(self.replacePB, 6, 2, 2, 1)
        self.label_2 = QtWidgets.QLabel(RenameTool)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 11, 0, 1, 1)
        self.line = QtWidgets.QFrame(RenameTool)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 10, 0, 1, 3)
        self.NewStringLE = QtWidgets.QLineEdit(RenameTool)
        self.NewStringLE.setObjectName("NewStringLE")
        self.gridLayout.addWidget(self.NewStringLE, 7, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.selectRB = QtWidgets.QRadioButton(RenameTool)
        self.selectRB.setChecked(True)
        self.selectRB.setObjectName("selectRB")
        self.buttonGroup_nameType = QtWidgets.QButtonGroup(RenameTool)
        self.buttonGroup_nameType.setObjectName("buttonGroup_nameType")
        self.buttonGroup_nameType.addButton(self.selectRB)
        self.horizontalLayout.addWidget(self.selectRB)
        self.hierarchyRB = QtWidgets.QRadioButton(RenameTool)
        self.hierarchyRB.setObjectName("hierarchyRB")
        self.buttonGroup_nameType.addButton(self.hierarchyRB)
        self.horizontalLayout.addWidget(self.hierarchyRB)
        self.allRb = QtWidgets.QRadioButton(RenameTool)
        self.allRb.setObjectName("allRb")
        self.buttonGroup_nameType.addButton(self.allRb)
        self.horizontalLayout.addWidget(self.allRb)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)
        self.SuffixLE = QtWidgets.QLineEdit(RenameTool)
        self.SuffixLE.setObjectName("SuffixLE")
        self.gridLayout.addWidget(self.SuffixLE, 12, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(RenameTool)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 12, 0, 1, 1)
        self.RenamePB = QtWidgets.QPushButton(RenameTool)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RenamePB.sizePolicy().hasHeightForWidth())
        self.RenamePB.setSizePolicy(sizePolicy)
        self.RenamePB.setObjectName("RenamePB")
        self.gridLayout.addWidget(self.RenamePB, 2, 2, 2, 1)
        self.label = QtWidgets.QLabel(RenameTool)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 2, 1)
        self.label_4 = QtWidgets.QLabel(RenameTool)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 1)
        self.OldStringLE = QtWidgets.QLineEdit(RenameTool)
        self.OldStringLE.setText("")
        self.OldStringLE.setObjectName("OldStringLE")
        self.gridLayout.addWidget(self.OldStringLE, 6, 1, 1, 1)
        self.remove_nameSpaceBT = QtWidgets.QPushButton(RenameTool)
        self.remove_nameSpaceBT.setObjectName("remove_nameSpaceBT")
        self.gridLayout.addWidget(self.remove_nameSpaceBT, 14, 0, 1, 3)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(RenameTool)
        QtCore.QMetaObject.connectSlotsByName(RenameTool)
        RenameTool.setTabOrder(self.selectRB, self.hierarchyRB)
        RenameTool.setTabOrder(self.hierarchyRB, self.allRb)
        RenameTool.setTabOrder(self.allRb, self.RenameLE)
        RenameTool.setTabOrder(self.RenameLE, self.RenamePB)
        RenameTool.setTabOrder(self.RenamePB, self.OldStringLE)
        RenameTool.setTabOrder(self.OldStringLE, self.NewStringLE)
        RenameTool.setTabOrder(self.NewStringLE, self.replacePB)
        RenameTool.setTabOrder(self.replacePB, self.prefixLE)
        RenameTool.setTabOrder(self.prefixLE, self.SuffixLE)
        RenameTool.setTabOrder(self.SuffixLE, self.add_pre_suffixPB)
        RenameTool.setTabOrder(self.add_pre_suffixPB, self.remove_pre_suffixPB)
        RenameTool.setTabOrder(self.remove_pre_suffixPB, self.check_duplicteNamePB)
        RenameTool.setTabOrder(self.check_duplicteNamePB, self.remove_nameSpaceBT)

    def retranslateUi(self, RenameTool):
        _translate = QtCore.QCoreApplication.translate
        RenameTool.setWindowTitle(_translate("RenameTool", "RenameTool"))
        self.add_pre_suffixPB.setText(_translate("RenameTool", "加前缀后缀"))
        self.remove_pre_suffixPB.setText(_translate("RenameTool", "删除前缀后缀"))
        self.check_duplicteNamePB.setText(_translate("RenameTool", "检查重名(选择重名)"))
        self.label_5.setText(_translate("RenameTool", "新字符"))
        self.replacePB.setText(_translate("RenameTool", "替换字符"))
        self.label_2.setText(_translate("RenameTool", "前缀"))
        self.selectRB.setText(_translate("RenameTool", "仅选中物体"))
        self.hierarchyRB.setText(_translate("RenameTool", "包括子物体"))
        self.allRb.setText(_translate("RenameTool", "All"))
        self.label_3.setText(_translate("RenameTool", "后缀"))
        self.RenamePB.setText(_translate("RenameTool", "重命名"))
        self.label.setText(_translate("RenameTool", "重命名"))
        self.label_4.setText(_translate("RenameTool", "旧字符"))
        self.remove_nameSpaceBT.setText(_translate("RenameTool", "去除命名空间"))
