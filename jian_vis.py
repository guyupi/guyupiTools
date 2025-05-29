# coding=utf-8
# 添加follow属性设置
import maya.cmds as  cmds

def add_wuqi_visAttr(ctrl, *args):
    # 添加属性
    cmds.addAttr(ctrl, longName="scabbard_Vis", keyable=True, attributeType='long', min=0, max=1, dv=1)
    for jianqiao in args[0]:
        cmds.connectAttr(ctrl + ".scabbard_Vis", jianqiao + ".visibility")
    for jian in args[1]:
        if jian in args[0]:
            jian_ofs = cmds.group(jian, n=jian + "_ofs")
            cmds.connectAttr(ctrl + ".sword_vis", jian_ofs + ".visibility")
        else:
            cmds.connectAttr(ctrl + ".sword_vis", jian + ".visibility")

#添加follow属性设置
#C:\Users\haoqiang\Documents\maya\scripts\guyupiTools\jian_vis.py
# import guyupiTools.jian_vis as jianvis
# reload(jianvis)
# import maya.cmds as  cmds
# ctrl = "weaponry_ctrl"
# jianbing = cmds.ls(sl = 1)
# list = []
# jian = cmds.ls(sl =1 )
# list.append(jianbing)
# list.append(jian)
# #for ctrl in sel:
# jianvis.add_wuqi_visAttr(ctrl ,*list)