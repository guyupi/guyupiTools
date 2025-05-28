#!/usr/bin/env python
# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel

# 选中根骨骼 创建出一条简模
def buid_meshJM(joint, JMwidth, direction , headOffect = False ,smooth = True):

    # 选中骨骼
    jointList = cmds.ls(joint, dag=True, type='joint')

    for jointHead in joint:

        jointList = cmds.ls(jointHead, dag=True, type='joint')

        if headOffect:
            tempjoint = cmds.createNode("joint" )
            cmds.matchTransform(tempjoint , jointHead ,piv = True ,pos = True,rot = True)
            cmds.setAttr(tempjoint + '.tx' , cmds.getAttr(tempjoint + ".tx") - cmds.getAttr(jointList[1] + ".tx"))
            jointList = [tempjoint] + jointList
        # 确定宽度，方向
        directionList = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        # 创建面片
        objectPlane = cmds.polyPlane(ch=1, object=1, axis=directionList[direction], w=JMwidth, h=JMwidth, sw=len(jointList) - 1, sh=1)[0]
        # 将面片的边与骨骼位置对应
        for num in range(1, len(jointList) + 1):
            if num < len(jointList):
                bian_num = 2 * num - 1
            else:
                bian_num = 2 * (num - 1)


            # 使用簇吸附到骨骼位置
            cluster = cmds.cluster(objectPlane + '.e['  + str(bian_num) + '] ')
            cmds.matchTransform(cluster, jointList[num - 1], pos=1, rot=1)

        # 删除历史
        cmds.select(objectPlane)
        cmds.DeleteHistory()
        if smooth:
            cmds.polySmooth(objectPlane , keepBorder = 0,divisions = 2)
        cmds.delete(tempjoint)




# 选中点拷贝出模型
def copyMesh(pointList=None):
    if "." in pointList[0]:
        vtxList = []
        old_mesh_name = pointList[0].split('.')[0]
        new_mesh_Name = cmds.duplicate(old_mesh_name)[0]

        # 将点序列转化为新模型的点序列
        for vtx in pointList:
            # new_mesh_Name = vtx.split(".")[0]
            vtx = vtx.replace(old_mesh_name, new_mesh_Name)
            vtxList.append(vtx)

        # 将模型的点转化为面，并获取所有的面数量，做减法，达到反选所有的面的效果
        connected_faces = cmds.polyListComponentConversion(vtxList, fromVertex=True, toFace=True)
        new_mod_face = cmds.ls(connected_faces, fl=True)

        new_mesh_numface = cmds.polyEvaluate(new_mesh_Name, face=True)
        setfirst = set(range(0, new_mesh_numface))
        setSceond = set()
        for face in new_mod_face:
            if ":" in face:
                rangeNumA = int(face.split("[")[1].split("]")[0].split(":")[0])
                rangeNumB = int(face.split("[")[1].split("]")[0].split(":")[1])
                setSceond.add(range(rangeNumA, rangeNumB))
            else:
                num = int(face.split('[')[1].split("]")[0])
                setSceond.add(num)

            # print setfirst,setSceond
        setfirst = setfirst - setSceond

        listFace = []

        for a in list(setfirst):
            listFace.append(new_mesh_Name + '.f[' + str(a) + ']')

        # print listFace
        cmds.select(listFace)
        cmds.polyDelFacet(listFace, ch=False)
    else:

        old_mesh_name = pointList[0].split('.')[0]
        new_mesh_Name = cmds.duplicate(old_mesh_name)[0]

    return new_mesh_Name

