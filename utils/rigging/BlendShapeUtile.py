# /usr/bin/env python
# -*- coding: UTF-8 -*-
#BlendShapeClass

import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import skinWeightUtils as skin
import OMapi
reload(skin)
reload(OMapi)


class BlendShapeClass(OMapi.API_base ,skin.SkinWeight):

    def __init__(self, mode=""):

        self.mode = mode
        self.BlendShapeNode = self.get_blendShapeNode()
        self.target = self.get_blendShapeTargets()
        # self.target_name = self.get_targetName()

    def __len__(self):
        return len(self.target)

    def __repr__(self):
        return self.BlendShapeNode

    def __str__(self):
        return self.BlendShapeNode

    def __getitem__(self, key):
        if isinstance(key, str) and key in self.target:
            return self.BlendShapeNode + "." + key
        elif isinstance(key, int):
            if key >= 0 & key < len(self.target):
                return self.BlendShapeNode + "." + self.target[key]

    def get_blendShapeNode(self):
        # 获取模型的blendshape节点
        geometryShape = cmds.listRelatives(self.mode, shapes=True) or []  # 获取模型的形状节点

        history = cmds.listHistory(geometryShape, il=2, pdo=False) or []
        blendshapes = [x for x in history if cmds.nodeType(x) == "blendShape"]
        if blendshapes:
            return blendshapes[0]
        else:
            return cmds.blendShape(self.mode , n = self.mode + "_bs")[0]


    def get_blendShape_Node(self , mode ):
        # 获取模型的blendshape节点
        geometryShape = cmds.listRelatives(mode, shapes=True) or []  # 获取模型的形状节点

        history = cmds.listHistory(geometryShape, il=2, pdo=False) or []
        blendshapes = [x for x in history if cmds.nodeType(x) == "blendShape"]
        if blendshapes:
            return blendshapes[0]
        else:
            return cmds.blendShape(mode ,  n = mode + "_bs")[0]

    # 获取节点中的所有目标提列表
    def get_blendShapeTargets(self):
        # 检查blendShape节点是否存在
        if not cmds.objExists(self.BlendShapeNode):
            cmds.error('{} 不存在。'.format(self.mode))
        # 获取BlendShape节点的所有目标
        targets = cmds.listAttr("{}.w".format(self.BlendShapeNode) , m=True)
        if not targets:
            targets = []
        return targets

    # def get_targetName(self):
    #     self.target_name = []
    #     if self.target == []:
    #         return self.target_name
    #     for name in self.target:
    #         # self.target_name.append(name.split('.')[1])
    #         print name

    # 获取节点中的所有目标提列表
    def get_blendShape_Targets(self , BlendShapeNode):
        # 检查blendShape节点是否存在
        if not cmds.objExists(BlendShapeNode):
            cmds.error('{} 不存在。'.format(BlendShapeNode))
        # 获取BlendShape节点的所有目标
        targets = cmds.listAttr("{}.w".format(BlendShapeNode), m=True)
        return targets

    # 更新列表
    def update_targetList(self):
        self.target = self.get_blendShapeTargets()
        # self.target_name = self.get_targetName()

    # 对模型添加target
    def add_Target(self, *args):
        repeat = []

        for num ,target in enumerate(args):
            if self.target:
                if target not in self.target:

                    cmds.blendShape(self.BlendShapeNode, edit=True,
                                    target=(self.mode, len(self.target), target, 1.0))
                else:
                    repeat.append(target)
            else:
                # target_list = list(args)[0]

                cmds.blendShape(self.BlendShapeNode, edit=True,
                                target=(self.mode, 0, target, 1.0))

            self.target.append(target)
        if repeat:
            cmds.error(u"目标体名称重叠 {}".format(repeat))

    # 反转target
    def flip_target(self, targetNum):
        # flip target
        cmds.blendShape(self.BlendShapeNode, e=True,
                        flipTarget=[(0, targetNum)],  # list of base and target pairs (0=base shape index)
                        mirrorDirection=0,  # 0=negative,1=positive
                        symmetrySpace=1,  # 0=topological, 1=object, 2=UV
                        symmetryAxis='x',  # for object symmetrySpace
                        )

    # 镜像target
    def mirror_target(self, targetNum):
        # mirror target
        cmds.blendShape(self.BlendShapeNode, e=True,
                        mirrorTarget=[(0, targetNum)],  # list of base and target pairs (0=base shape index)
                        mirrorDirection=0,  # 0=negative,1=positive
                        symmetrySpace=1,  # 0=topological, 1=object, 2=UV
                        symmetryAxis='x',  # for object symmetrySpace
                        )

    # 复制target
    def duplicte_target(self, *args):
        # cmds.blendShape(self.BlendShapeNode, edit=True, ib=True, target=[self.mode, len(self.target), target, 0.0])
        self.update_targetList()

    # 添加target
    def add_combinationTarget(self, *args):
        self.update_targetList()
        pass

    # 移除目标体
    def remove_target(self, num):
        cmds.blendShape(self.BlendShapeNode, edit=True, remove=True,
                        target=[self.mode, len(self.target), self[num].split(".")[1], 0.0])
        self.update_targetList()

    # 提取目标体
    def extract_target(self, num):

        if not cmds.objExists(self.BlendShapeNode + "_Target_grp"):
            target_grp = cmds.createNode("transform", n=(self.BlendShapeNode + "_Target_grp"))

        target = cmds.sculptTarget("blendShape3", e=True, regenerate=True, target=2)[0]
        cmds.parent(target, (self.BlendShapeNode + "_Target_grp"))
        self.update_targetList()

    # 获取单个目标体链接的节点与属性名称
    def get_targetConnect(self, num):
        connectNode = cmds.listConnections(self[num], source=True, plugs=True) or []
        return connectNode

    # 获取目标体的位移节点
    def get_targetVtxId(self, targetNum):
        # print '{}.inputTarget[{}].inputTargetGroup[{}].inputTargetItem[{}].inputComponentsTarget'.format(self.BlendShapeNode , targetNum , targetNum , 6000+targetNum)
        return cmds.getAttr('{}.inputTarget[{}].inputTargetGroup[{}].inputTargetItem[{}].inputComponentsTarget'.format(
            self.BlendShapeNode, targetNum, targetNum, 6000 + targetNum))

    # 获取目标体每个点位移的向量
    def get_targetVtxVector(self, targetNum):
        # print '{}.inputTarget[{}].inputTargetGroup[{}].inputTargetItem[{}].inputPointsTarget'.format(self.BlendShapeNode , targetNum , targetNum , 6000+targetNum)
        return cmds.getAttr(
            '{}.inputTarget[{}].inputTargetGroup[{}].inputTargetItem[{}].inputPointsTarget'.format(self.BlendShapeNode,
                                                                                                   targetNum, targetNum,
                                                                                                   6000 + targetNum))

    # 获取链接链接属性
    def copy_connectAttr(self):

        sources_list = []
        for num , target in enumerate(self.target):
            sources = cmds.listConnections(self[num], d=False, p=True)
            islock = cmds.getAttr(self[num], l=True)
            value = cmds.getAttr(self[num])

            if sources:
                sources_list.append([sources[0],self[num] , islock, value])
            else:
                sources_list.append([None,self[num] , islock, value])

        return sources_list

    #设置链接属性
    def paste_connectAttr(self,mesh , sources_list ):

        #获取mesh的信息
        mesh_bs = self.get_blendShape_Node(mesh)
        mesh_bs_target = self.get_blendShape_Targets(mesh_bs)
        # sources_list 的构成是[sources[0],self[num] , islock, value]
        for sources in sources_list:
            target_B = sources[1].split(".")[1]
            # if target_B in mesh_bs_target:
            cmds.setAttr(mesh_bs + "." + target_B , sources[3])
            if sources[0]:
                cmds.connectAttr(sources[0] , mesh_bs + "." + target_B)
            cmds.setAttr(mesh_bs + "." + target_B , l = sources[2] )

class edite_Deform(OMapi.API_base ,skin.SkinWeight):

    def __init__(self , mode , deform):

        self.mode = mode
        self.deform = deform

    # 导出bs封套
    def export_bs_wei(self):

        defmObj = self.get_MDependNode(self.deform)

        vtx = cmds.ls("{}.vtx[*]".format(self.mode), fl=1)

        modelPth, compsObj = self.get_vtxMobject(self.mode ,vtx)

        wetsArray = om.MFloatArray()

        wetFilterFn = oma.MFnWeightGeometryFilter(defmObj)

        wetFilterFn.getWeights(modelPth , compsObj ,wetsArray)

        return wetsArray

    # def move_jointWeightsToDeform(self,deform, model, vertexs, weights):
    #     """
    #     deform :  变形器名称  允许cluster flexors, and user-defined deformers
    #     """
    #     defmObj = self.get_MDependNode(deform)
    #     modelPth, compsObj = self.get_vtxMobject(model, vertexs)
    #
    #     # print(defmObj)
    #
    #     # Build weight float array
    #     wetsArray = om.MFloatArray()
    #     for v in weights:
    #         wetsArray.append(v)
    #     # Set weights once
    #     wetFilterFn = oma.MFnWeightGeometryFilter(defmObj)
    #
    #     try:
    #         wetFilterFn.setWeight(modelPth, compsObj, wetsArray)
    #     except:
    #         raise Warning(deform, model, vertexs)
    #     return True