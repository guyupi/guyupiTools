#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtWidgets
from maya import cmds
import json
import os


class PluginSettingsManager(object):
    """
    Maya 插件设置管理类
    用于保存和读取插件的各种设置
    """

    def __init__(self, plugin_name):
        """
        初始化设置管理器

        :param plugin_name: 插件名称，用于创建唯一的设置存储路径
        """
        self.plugin_name = plugin_name
        self.settings_folder = self._get_settings_folder()

        # 确保设置文件夹存在
        if not os.path.exists(self.settings_folder):
            os.makedirs(self.settings_folder)

    def _get_settings_folder(self):
        """
        获取插件设置存储的文件夹路径

        :return: 设置文件夹的完整路径
        """
        maya_app_dir = cmds.internalVar(userAppDir=True)
        return os.path.join(maya_app_dir, "prefs", "pluginSettings", self.plugin_name)

    def save_setting(self, setting_name, data):
        """
        保存设置到文件

        :param setting_name: 设置名称(将用作文件名)
        :param data: 要保存的数据(可以是字典、列表等可JSON序列化的数据)
        :return: 保存的文件路径
        """
        setting_file = os.path.join(self.settings_folder, "{0}.json".format(setting_name))

        try:
            with open(setting_file, 'w') as f:
                json.dump(data, f, indent=4)
            return setting_file
        except Exception as e:
            cmds.warning("Failed to save setting {0}: {1}".format(setting_name, str(e)))
            return None

    def load_setting(self, setting_name, default=None):
        """
        从文件加载设置

        :param setting_name: 要加载的设置名称
        :param default: 如果设置不存在时返回的默认值
        :return: 加载的数据或默认值
        """
        setting_file = os.path.join(self.settings_folder, "{0}.json".format(setting_name))

        if not os.path.exists(setting_file):
            return default

        try:
            with open(setting_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            cmds.warning("Failed to load setting {0}: {1}".format(setting_name, str(e)))
            return default

    def save_ui_settings(self, ui_widget, setting_name="ui_settings"):
        """
        保存UI控件的状态和值

        :param ui_widget: PySide2 UI控件
        :param setting_name: 设置名称
        """
        settings = {}

        # 保存窗口几何信息
        if hasattr(ui_widget, 'saveGeometry'):
            settings['geometry'] = ui_widget.saveGeometry().toBase64().data()

        # 保存所有子控件的状态
        for child in ui_widget.findChildren(QtCore.QObject):
            if hasattr(child, 'objectName') and child.objectName():
                obj_name = child.objectName()

                # QCheckBox
                if isinstance(child, QtWidgets.QCheckBox):
                    settings[obj_name] = child.isChecked()

                # QLineEdit, QTextEdit
                elif isinstance(child, (QtWidgets.QLineEdit, QtWidgets.QTextEdit)):
                    settings[obj_name] = child.text()

                # QComboBox
                elif isinstance(child, QtWidgets.QComboBox):
                    settings[obj_name] = child.currentIndex()

                # QSpinBox, QDoubleSpinBox
                elif isinstance(child, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
                    settings[obj_name] = child.value()

                # QSlider
                elif isinstance(child, QtWidgets.QSlider):
                    settings[obj_name] = child.value()

                # QRadioButton
                elif isinstance(child, QtWidgets.QRadioButton):
                    settings[obj_name] = child.isChecked()

        return self.save_setting(setting_name, settings)

    def load_ui_settings(self, ui_widget, setting_name="ui_settings"):
        """
        加载UI控件的状态和值

        :param ui_widget: PySide2 UI控件
        :param setting_name: 设置名称
        """
        settings = self.load_setting(setting_name, {})
        if not settings:
            return False

        # 恢复窗口几何信息
        if 'geometry' in settings and hasattr(ui_widget, 'restoreGeometry'):
            geometry = QtCore.QByteArray.fromBase64(settings['geometry'])
            ui_widget.restoreGeometry(geometry)

        # 恢复所有子控件的状态
        for child in ui_widget.findChildren(QtCore.QObject):
            if hasattr(child, 'objectName') and child.objectName():
                obj_name = child.objectName()

                if obj_name not in settings:
                    continue

                value = settings[obj_name]

                # QCheckBox
                if isinstance(child, QtWidgets.QCheckBox):
                    child.setChecked(bool(value))

                # QLineEdit, QTextEdit
                elif isinstance(child, (QtWidgets.QLineEdit, QtWidgets.QTextEdit)):
                    child.setText(str(value))

                # QComboBox
                elif isinstance(child, QtWidgets.QComboBox):
                    try:
                        child.setCurrentIndex(int(value))
                    except:
                        pass

                # QSpinBox, QDoubleSpinBox
                elif isinstance(child, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
                    child.setValue(float(value))

                # QSlider
                elif isinstance(child, QtWidgets.QSlider):
                    child.setValue(int(value))

                # QRadioButton
                elif isinstance(child, QtWidgets.QRadioButton):
                    child.setChecked(bool(value))

        return True