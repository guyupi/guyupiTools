import sys
import json
import os
from PySide2.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QCheckBox, QComboBox, QSlider)
from PySide2.QtCore import Qt, QSettings


class SettingsManager:

    """设置管理类，负责保存和读取界面设置"""

    def __init__(self, app_name, settings_file="settings.json"):
        self.app_name = app_name
        self.settings_file = settings_file
        self.settings = {}

    def save_settings(self, window):
        """保存窗口和控件设置"""
        # 保存窗口状态
        self.settings["window_geometry"] = self._window_geometry_to_dict(window)
        self.settings["window_state"] = window.saveState()

        # 保存控件状态（示例：只保存QCheckBox和QComboBox）
        self.settings["controls"] = {}
        self._save_controls(window, self.settings["controls"])

        # 保存到文件
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def load_settings(self, window):
        """加载窗口和控件设置"""
        if not os.path.exists(self.settings_file):
            return

        with open(self.settings_file, 'r', encoding='utf-8') as f:
            self.settings = json.load(f)

        # 恢复窗口状态
        if "window_geometry" in self.settings:
            window.restoreGeometry(self._dict_to_window_geometry(self.settings["window_geometry"]))

        if "window_state" in self.settings:
            window.restoreState(self.settings["window_state"])

        # 恢复控件状态
        if "controls" in self.settings:
            self._load_controls(window, self.settings["controls"])

    def _window_geometry_to_dict(self, window):
        """将窗口几何信息转换为字典"""
        geo = window.geometry()
        return {
            "x": geo.x(),
            "y": geo.y(),
            "width": geo.width(),
            "height": geo.height()
        }

    def _dict_to_window_geometry(self, dict_data):
        """将字典转换为窗口几何信息"""
        from PyQt5.QtCore import QRect
        return QRect(dict_data["x"], dict_data["y"],
                     dict_data["width"], dict_data["height"])

    def _save_controls(self, parent, controls_dict):
        """递归保存控件状态"""
        for child in parent.findChildren(QWidget):
            obj_name = child.objectName()
            if not obj_name:
                continue

            # 保存复选框状态
            if isinstance(child, QCheckBox):
                controls_dict[obj_name] = {
                    "type": "QCheckBox",
                    "checked": child.isChecked()
                }
            # 保存下拉框选择
            elif isinstance(child, QComboBox):
                controls_dict[obj_name] = {
                    "type": "QComboBox",
                    "current_index": child.currentIndex(),
                    "items": [child.itemText(i) for i in range(child.count())]
                }
            # 保存滑块值
            elif isinstance(child, QSlider):
                controls_dict[obj_name] = {
                    "type": "QSlider",
                    "value": child.value()
                }

            # 递归处理子控件
            self._save_controls(child, controls_dict)

    def _load_controls(self, parent, controls_dict):
        """递归加载控件状态"""
        for child in parent.findChildren(QWidget):
            obj_name = child.objectName()
            if obj_name in controls_dict:
                ctrl_settings = controls_dict[obj_name]

                # 恢复复选框状态
                if ctrl_settings["type"] == "QCheckBox" and isinstance(child, QCheckBox):
                    child.setChecked(ctrl_settings["checked"])
                # 恢复下拉框选择
                elif ctrl_settings["type"] == "QComboBox" and isinstance(child, QComboBox):
                    # 先清空再添加项目（确保项目顺序一致）
                    child.clear()
                    child.addItems(ctrl_settings["items"])
                    # 设置当前索引
                    if ctrl_settings["current_index"] < child.count():
                        child.setCurrentIndex(ctrl_settings["current_index"])
                # 恢复滑块值
                elif ctrl_settings["type"] == "QSlider" and isinstance(child, QSlider):
                    child.setValue(ctrl_settings["value"])

            # 递归处理子控件
            self._load_controls(child, controls_dict)

