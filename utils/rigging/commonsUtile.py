# /usr/bin/env python
# -*- coding: UTF-8 -*-
import maya.cmds as cmds



# 创建根据曲线创建点控制的loc
def createLocForCurve(curve):
    curve_shape = cmds.listRelatives(curve, shapes=True)[0]

    # 获取曲线的度数和跨度
    spans = cmds.getAttr(curve_shape + '.spans')

    if not cmds.objExists('loc_{}_grp'.format(curve)):
        cmds.group(em=True, name='loc_{}_grp'.format(curve))

    locList = []
    # 创建簇和定位器，并设置约束
    for i in range(spans):
        # 创建定位器到每个对应的cv点上，并把他p给loc的组
        cv = curve + '.cv[' + str(i) + ']'
        point_SpaceWorld = cmds.xform(cv, q=True, translation=True, ws=True)

        loc = cmds.spaceLocator(name='loc_{}_{}'.format(i, curve))[0]
        # loc_tran = cmds.listRelatives(loc, p=True)
        # print loc
        cmds.move(point_SpaceWorld[0], point_SpaceWorld[1], point_SpaceWorld[2], loc)
        cmds.parent(loc, 'loc_{}_grp'.format(curve))
        locList.append(loc)
        # 创建最近点节点
        nearestPoint_node = cmds.createNode('nearestPointOnCurve', name='NearestPoint_{}_{}'.format(i, curve))
        pointOnCur_node = cmds.createNode('pointOnCurveInfo', name='PointOnCur_{}_{}'.format(i, curve))

        # 连接曲线、定位器和最近点节点
        cmds.connectAttr(curve + '.worldSpace[0]', nearestPoint_node + '.inputCurve', force=True)
        cmds.connectAttr(loc + '.translate', nearestPoint_node + '.inPosition', force=True)

        # 获取参数值
        par = cmds.getAttr(nearestPoint_node + '.parameter')

        # # 连接曲线和定位器节点
        cmds.connectAttr(curve + '.worldSpace[0]', pointOnCur_node + '.inputCurve', force=True)
        cmds.setAttr(pointOnCur_node + '.parameter', par)
        cmds.connectAttr(pointOnCur_node + '.position', loc + '.translate', force=True)

        # 删除最近点节点
        cmds.delete(nearestPoint_node)

    return ('loc_{}_grp'.format(curve)), locList

#判断世界坐标
def get_worldSpaceToLF(obj = "" ,plane = 0):
    space = cmds.xform(obj , q = True , translation = True ,worldSpace =True)
    if space[plane] > 0.1:
        return "l"
    elif space[plane] < 0.1:
        return "r"
    else:
        return "m"

def get_sceneSizeforMesh():

    objects = cmds.ls(type="mesh", dag=True)
    if objects:
        # 获取所有物体组合后的边界框
        bbox = cmds.exactWorldBoundingBox(*objects)

        size = float(bbox[3] - bbox[0] + bbox[4] - bbox[1] + bbox[5] - bbox[2]) / 3

        return size
    else:
        size = 10
        return size