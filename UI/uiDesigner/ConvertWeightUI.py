# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ConvertWeightUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide2 import QtCore, QtGui, QtWidgets


class Ui_ConvertWeightTool(object):
    def setupUi(self, ConvertWeightTool):
        ConvertWeightTool.setObjectName("ConvertWeightTool")
        ConvertWeightTool.resize(506, 438)
        self.verticalLayout = QtWidgets.QVBoxLayout(ConvertWeightTool)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(4, 4, 4, 4)
        self.gridLayout.setHorizontalSpacing(5)
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setObjectName("gridLayout")
        self.oneByOneRB = QtWidgets.QRadioButton(ConvertWeightTool)
        self.oneByOneRB.setObjectName("oneByOneRB")
        self.buttonGroup_weightTtype = QtWidgets.QButtonGroup(ConvertWeightTool)
        self.buttonGroup_weightTtype.setObjectName("buttonGroup_weightTtype")
        self.buttonGroup_weightTtype.addButton(self.oneByOneRB)
        self.gridLayout.addWidget(self.oneByOneRB, 4, 1, 1, 1)
        self.RootJointLE_loadBt = QtWidgets.QPushButton(ConvertWeightTool)
        self.RootJointLE_loadBt.setObjectName("RootJointLE_loadBt")
        self.gridLayout.addWidget(self.RootJointLE_loadBt, 1, 3, 1, 1)
        self.offsetOneRB = QtWidgets.QRadioButton(ConvertWeightTool)
        self.offsetOneRB.setChecked(True)
        self.offsetOneRB.setObjectName("offsetOneRB")
        self.buttonGroup_weightTtype.addButton(self.offsetOneRB)
        self.gridLayout.addWidget(self.offsetOneRB, 4, 2, 1, 1)
        self.offsetEndRB = QtWidgets.QRadioButton(ConvertWeightTool)
        self.offsetEndRB.setObjectName("offsetEndRB")
        self.buttonGroup_weightTtype.addButton(self.offsetEndRB)
        self.gridLayout.addWidget(self.offsetEndRB, 4, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(ConvertWeightTool)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.ChildrenLe_loadBt = QtWidgets.QPushButton(ConvertWeightTool)
        self.ChildrenLe_loadBt.setObjectName("ChildrenLe_loadBt")
        self.gridLayout.addWidget(self.ChildrenLe_loadBt, 2, 3, 1, 1)
        self.label = QtWidgets.QLabel(ConvertWeightTool)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.meshLE_loadBt = QtWidgets.QPushButton(ConvertWeightTool)
        self.meshLE_loadBt.setObjectName("meshLE_loadBt")
        self.gridLayout.addWidget(self.meshLE_loadBt, 0, 3, 1, 1)
        self.label_3 = QtWidgets.QLabel(ConvertWeightTool)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.RootJointListLE_loadBt = QtWidgets.QPushButton(ConvertWeightTool)
        self.RootJointListLE_loadBt.setObjectName("RootJointListLE_loadBt")
        self.gridLayout.addWidget(self.RootJointListLE_loadBt, 3, 3, 1, 1)
        self.RootJointListLE = QtWidgets.QLineEdit(ConvertWeightTool)
        self.RootJointListLE.setReadOnly(True)
        self.RootJointListLE.setObjectName("RootJointListLE")
        self.gridLayout.addWidget(self.RootJointListLE, 3, 1, 1, 2)
        self.meshLE = QtWidgets.QLineEdit(ConvertWeightTool)
        self.meshLE.setReadOnly(True)
        self.meshLE.setObjectName("meshLE")
        self.gridLayout.addWidget(self.meshLE, 0, 1, 1, 2)
        self.RootJointLE = QtWidgets.QLineEdit(ConvertWeightTool)
        self.RootJointLE.setReadOnly(True)
        self.RootJointLE.setObjectName("RootJointLE")
        self.gridLayout.addWidget(self.RootJointLE, 1, 1, 1, 2)
        self.IntegratedWeightPB = QtWidgets.QPushButton(ConvertWeightTool)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IntegratedWeightPB.sizePolicy().hasHeightForWidth())
        self.IntegratedWeightPB.setSizePolicy(sizePolicy)
        self.IntegratedWeightPB.setObjectName("IntegratedWeightPB")
        self.gridLayout.addWidget(self.IntegratedWeightPB, 8, 0, 1, 4)
        self.label_6 = QtWidgets.QLabel(ConvertWeightTool)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.ConvertWeightPB = QtWidgets.QPushButton(ConvertWeightTool)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ConvertWeightPB.sizePolicy().hasHeightForWidth())
        self.ConvertWeightPB.setSizePolicy(sizePolicy)
        self.ConvertWeightPB.setObjectName("ConvertWeightPB")
        self.gridLayout.addWidget(self.ConvertWeightPB, 7, 0, 1, 4)
        self.curveTypeARB = QtWidgets.QRadioButton(ConvertWeightTool)
        self.curveTypeARB.setObjectName("curveTypeARB")
        self.buttonGroup_curveType = QtWidgets.QButtonGroup(ConvertWeightTool)
        self.buttonGroup_curveType.setObjectName("buttonGroup_curveType")
        self.buttonGroup_curveType.addButton(self.curveTypeARB)
        self.gridLayout.addWidget(self.curveTypeARB, 5, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(ConvertWeightTool)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.curveTypeBRB = QtWidgets.QRadioButton(ConvertWeightTool)
        self.curveTypeBRB.setObjectName("curveTypeBRB")
        self.buttonGroup_curveType.addButton(self.curveTypeBRB)
        self.gridLayout.addWidget(self.curveTypeBRB, 5, 2, 1, 1)
        self.curveTypeCRB = QtWidgets.QRadioButton(ConvertWeightTool)
        self.curveTypeCRB.setChecked(True)
        self.curveTypeCRB.setObjectName("curveTypeCRB")
        self.buttonGroup_curveType.addButton(self.curveTypeCRB)
        self.gridLayout.addWidget(self.curveTypeCRB, 5, 3, 1, 1)
        self.RootJointListCB = QtWidgets.QCheckBox(ConvertWeightTool)
        self.RootJointListCB.setChecked(False)
        self.RootJointListCB.setTristate(False)
        self.RootJointListCB.setObjectName("RootJointListCB")
        self.gridLayout.addWidget(self.RootJointListCB, 3, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(ConvertWeightTool)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.ChildrenLe = QtWidgets.QLineEdit(ConvertWeightTool)
        self.ChildrenLe.setReadOnly(True)
        self.ChildrenLe.setObjectName("ChildrenLe")
        self.gridLayout.addWidget(self.ChildrenLe, 2, 1, 1, 2)
        self.percent_spinBox = QtWidgets.QSpinBox(ConvertWeightTool)
        self.percent_spinBox.setMaximum(100)
        self.percent_spinBox.setProperty("value", 80)
        self.percent_spinBox.setObjectName("percent_spinBox")
        self.gridLayout.addWidget(self.percent_spinBox, 6, 1, 1, 3)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(ConvertWeightTool)
        QtCore.QMetaObject.connectSlotsByName(ConvertWeightTool)
        ConvertWeightTool.setTabOrder(self.offsetEndRB, self.RootJointListCB)
        ConvertWeightTool.setTabOrder(self.RootJointListCB, self.offsetOneRB)
        ConvertWeightTool.setTabOrder(self.offsetOneRB, self.meshLE_loadBt)
        ConvertWeightTool.setTabOrder(self.meshLE_loadBt, self.RootJointLE_loadBt)
        ConvertWeightTool.setTabOrder(self.RootJointLE_loadBt, self.ChildrenLe_loadBt)
        ConvertWeightTool.setTabOrder(self.ChildrenLe_loadBt, self.RootJointListLE_loadBt)
        ConvertWeightTool.setTabOrder(self.RootJointListLE_loadBt, self.curveTypeARB)
        ConvertWeightTool.setTabOrder(self.curveTypeARB, self.curveTypeBRB)
        ConvertWeightTool.setTabOrder(self.curveTypeBRB, self.curveTypeCRB)
        ConvertWeightTool.setTabOrder(self.curveTypeCRB, self.ConvertWeightPB)
        ConvertWeightTool.setTabOrder(self.ConvertWeightPB, self.IntegratedWeightPB)
        ConvertWeightTool.setTabOrder(self.IntegratedWeightPB, self.meshLE)
        ConvertWeightTool.setTabOrder(self.meshLE, self.RootJointLE)
        ConvertWeightTool.setTabOrder(self.RootJointLE, self.ChildrenLe)
        ConvertWeightTool.setTabOrder(self.ChildrenLe, self.RootJointListLE)
        ConvertWeightTool.setTabOrder(self.RootJointListLE, self.percent_spinBox)
        ConvertWeightTool.setTabOrder(self.percent_spinBox, self.oneByOneRB)

    def retranslateUi(self, ConvertWeightTool):
        _translate = QtCore.QCoreApplication.translate
        ConvertWeightTool.setWindowTitle(_translate("ConvertWeightTool", "ConvertWeightTool"))
        self.oneByOneRB.setText(_translate("ConvertWeightTool", "一对一"))
        self.RootJointLE_loadBt.setText(_translate("ConvertWeightTool", "<<"))
        self.offsetOneRB.setText(_translate("ConvertWeightTool", "偏移"))
        self.offsetEndRB.setText(_translate("ConvertWeightTool", "偏移加末端"))
        self.label_2.setText(_translate("ConvertWeightTool", "根骨骼"))
        self.ChildrenLe_loadBt.setText(_translate("ConvertWeightTool", "<<"))
        self.label.setText(_translate("ConvertWeightTool", "模型"))
        self.meshLE_loadBt.setText(_translate("ConvertWeightTool", "<<"))
        self.label_3.setText(_translate("ConvertWeightTool", "子骨骼"))
        self.RootJointListLE_loadBt.setText(_translate("ConvertWeightTool", "<<"))
        self.IntegratedWeightPB.setText(_translate("ConvertWeightTool", "整合权重"))
        self.label_6.setText(_translate("ConvertWeightTool", "曲线类型"))
        self.ConvertWeightPB.setText(_translate("ConvertWeightTool", "分配权重"))
        self.curveTypeARB.setText(_translate("ConvertWeightTool", "1 Linear"))
        self.label_7.setText(_translate("ConvertWeightTool", "柔软度"))
        self.curveTypeBRB.setText(_translate("ConvertWeightTool", "2"))
        self.curveTypeCRB.setText(_translate("ConvertWeightTool", "3 Cubic"))
        self.RootJointListCB.setText(_translate("ConvertWeightTool", "根骨骼列表"))
        self.label_5.setText(_translate("ConvertWeightTool", "权重分配类型"))
