# /usr/bin/env python
# -*- coding: UTF-8 -*-
# BlendShapeTool
import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMaya as om
from ..rigging import nameUtils
from ..rigging import BlendShapeUtile
from ..rigging import skinWeightUtils

reload(BlendShapeUtile)
reload(nameUtils)

class CopyBlendShapeTool(BlendShapeUtile.BlendShapeClass):

    def __init__(self, base_Mode, target_mode, mirror_target=''):
        super(CopyBlendShapeTool, self).__init__(base_Mode)
        self.base_Mode = base_Mode
        self.mide_mode = "CopyBSTooL_temp_midMode"
        self.target_mode = target_mode
        self.mirror_target = mirror_target

    # def createWrap(self, *args, **kwargs):
    #     influence = args[0]
    #     surface = args[1]
    #
    #     shapes = cmds.listRelatives(influence, shapes=True)
    #     influenceShape = shapes[0]
    #
    #     shapes = cmds.listRelatives(surface, shapes=True)
    #     surfaceShape = shapes[0]
    #
    #     weightThreshold = kwargs.get('weightThreshold', 0.0)
    #     maxDistance = kwargs.get('maxDistance', 1.0)
    #     exclusiveBind = kwargs.get('exclusiveBind', False)
    #     autoWeightThreshold = kwargs.get('autoWeightThreshold', True)
    #     falloffMode = kwargs.get('falloffMode', 0)
    #
    #     wrapData = cmds.deformer(surface, type='wrap')
    #     wrapNode = wrapData[0]
    #
    #     cmds.setAttr(wrapNode + '.weightThreshold', weightThreshold)
    #     cmds.setAttr(wrapNode + '.maxDistance', maxDistance)
    #     cmds.setAttr(wrapNode + '.exclusiveBind', exclusiveBind)
    #     cmds.setAttr(wrapNode + '.autoWeightThreshold', autoWeightThreshold)
    #     cmds.setAttr(wrapNode + '.falloffMode', falloffMode)
    #
    #     cmds.connectAttr(surface + '.worldMatrix[0]', wrapNode + '.geomMatrix')
    #
    #     duplicateData = cmds.duplicate(influence, name=influence + 'Base')
    #     base = duplicateData[0]
    #     shapes = cmds.listRelatives(base, shapes=True)
    #     baseShape = shapes[0]
    #     cmds.hide(base)
    #
    #     if not cmds.attributeQuery('dropoff', n=influence, exists=True):
    #         cmds.addAttr(influence, sn='dr', ln='dropoff', dv=4.0, min=0.0, max=20.0)
    #         cmds.setAttr(influence + '.dr', k=True)
    #
    #     if cmds.nodeType(influenceShape) == 'mesh':
    #         if not cmds.attributeQuery('smoothness', n=influence, exists=True):
    #             cmds.addAttr(influence, sn='smt', ln='smoothness', dv=0.0, min=0.0)
    #             cmds.setAttr(influence + '.smt', k=True)
    #
    #         if not cmds.attributeQuery('inflType', n=influence, exists=True):
    #             cmds.addAttr(influence, at='short', sn='ift', ln='inflType', dv=2, min=1, max=2)
    #
    #         cmds.connectAttr(influenceShape + '.worldMesh', wrapNode + '.driverPoints[0]')
    #         cmds.connectAttr(baseShape + '.worldMesh', wrapNode + '.basePoints[0]')
    #         cmds.connectAttr(influence + '.inflType', wrapNode + '.inflType[0]')
    #         cmds.connectAttr(influence + '.smoothness', wrapNode + '.smoothness[0]')
    #
    #     if cmds.nodeType(influenceShape) == 'nurbsCurve' or cmds.nodeType(influenceShape) == 'nurbsSurface':
    #         if not cmds.attributeQuery('wrapSamples', n=influence, exists=True):
    #             cmds.addAttr(influence, at='short', sn='wsm', ln='wrapSamples', dv=10, min=1)
    #             cmds.setAttr(influence + '.wsm', k=True)
    #
    #         cmds.connectAttr(influenceShape + '.ws', wrapNode + '.driverPoints[0]')
    #         cmds.connectAttr(baseShape + '.ws', wrapNode + '.basePoints[0]')
    #         cmds.connectAttr(influence + '.wsm', wrapNode + '.nurbsSamples[0]')
    #
    #     cmds.connectAttr(influence + '.dropoff', wrapNode + '.dropoff[0]')
    #     return wrapNode

    def createWrap(self ,medium ,source ,setmode):
        cmds.select( source,medium, r=True)
        mel.eval("doWrapArgList \"7\"{\"1\", \"0\", \"1\", \"2\", \"%s\", \"1\", \"0\", \"0\"};" % setmode)

    # 复制形态的函数
    def copy_Mesh(self, mode, new_name):
        return cmds.duplicate(mode, n=new_name)[0]

    # 创建介质的函数
    def create_MidMode(self):
        if not cmds.objExists("temp_copybsTool_grp_001"):
            cmds.createNode("transform", n="temp_copybsTool_grp_001")
        if not cmds.objExists(self.mide_mode):
            self.copy_Mesh(self.target_mode, self.mide_mode)

        cmds.parent(self.mide_mode, "temp_copybsTool_grp_001")

    # 镜像功能实现
    def create_mirrorMidMode(self):

        if not cmds.objExists("temp_copybsTool_grp_001"):
            cmds.createNode("transform", n="temp_copybsTool_grp_001")

        if not cmds.objExists(self.mide_mode):
            self.copy_Mesh(self.base_Mode, self.base_Mode + "_temp")

        base_modeBsNode = cmds.blendShape(self.base_Mode ,self.base_Mode + "_temp" )[0]

        cmds.createNode("transform", n="file_mirror_grp")
        cmds.parent(self.base_Mode + "_temp", "file_mirror_grp" )
        cmds.parent("file_mirror_grp" , "temp_copybsTool_grp_001")
        cmds.setAttr("file_mirror_grp.sx", -1)
        cmds.setAttr(base_modeBsNode + "." + self.base_Mode, 1)
        self.target_mode = self.copy_Mesh(self.mirror_target , self.mide_mode)
        cmds.parent(self.mide_mode , "temp_copybsTool_grp_001")

        # 创建包裹的函数
    def create_Warp(self, deltaMush=False, exclusiveBind=False ,mirror = False):

        if not cmds.objExists(self.mide_mode):
            cmds.error(u"生成介质后才能进行包裹")
        exclusiveBind = int(exclusiveBind)
        # cmds.setAttr(self.BlendShapeNode + ".envelope" , 0)
        if mirror:
            self.createWrap(self.base_Mode + "_temp", self.mide_mode,exclusiveBind)
        else:
            self.createWrap(self.base_Mode, self.mide_mode, exclusiveBind)
        if deltaMush:
            dmNode = cmds.deltaMush(self.medium, si=10, ss=0.5, pbv=True, en=1)
            cmds.select(dmNode, r=True)
        # cmds.setAttr(self.BlendShapeNode + ".envelope" , 1)

    # 传递bs的函数
    def transfer_bs(self, unlock=False ,mirror = False):
        """
        :param unlock: 是否跳过已经锁定的属性
        :return:
        """
        if not mirror:
            mide_bs = self.get_blendShape_Node(self.target_mode)

            if self.get_blendShape_Targets(mide_bs):
                cmds.delete(mide_bs)
                mide_bs = self.get_blendShape_Node(self.target_mode)

        # 遍历所有的target从0-1的过程复制出形态传递给target_mode
        # 先将模型的target全部都归零 并获取链接节点的名称
        sources_list = []  # 储存：链接对象，链接是否锁定，链接属性,属性原本的值
        for num, target in enumerate(self.target):
            # 将target的数值改为0
            sources = cmds.listConnections(self[num], d=False, p=True)
            islock = cmds.getAttr(self[num], l=True)
            value = cmds.getAttr(self[num])
            # cmds.disconnectAttr(self[num] , sources)
            if unlock and islock == unlock:
                continue
            if sources:
                sources_list.append([sources[0], islock, self[num], value])
                cmds.setAttr(self[num], l=False)
                cmds.disconnectAttr(sources[0], self[num])
            else:
                sources_list.append([None, islock, self[num], value])


        temp_targetList = []
        target_nameList = []
        # #提取出形态
        for num, list_t in enumerate(sources_list):
            if unlock and unlock == list_t[1]:
                continue
            else:
                cmds.setAttr(sources_list[num][2], 1)

                new_target = self.copy_Mesh(self.mide_mode ,  sources_list[num][2].split(".")[1])

                # print new_target ,sources_list[num]
                # nameUtils.Name.uuid_rename(new_target , sources_list[num][2].split(".")[1])

                temp_targetList.append(new_target)

                target_nameList.append(sources_list[num][2].split(".")[1])

                cmds.setAttr(sources_list[num][2], 0)


        # 镜像的形态保留，
        if mirror:
            mirror_grp = cmds.createNode("transform", n="{}_mirror_target".format(self.mirror_target))
            cmds.parent(temp_targetList, mirror_grp)
            # 恢复链接
            for num, obj_list in enumerate(sources_list):
                if obj_list[0]:
                    cmds.connectAttr(obj_list[0], obj_list[2])
                else:
                    cmds.setAttr(obj_list[2], obj_list[3])
                if obj_list[1]:
                    cmds.setAttr(obj_list[2], l=True)
        else:
            #直接传递的需要构建blendshape, 将形态放到对应的blenshape里面，并恢复链接
            for num, obj_list in enumerate(sources_list):


                cmds.blendShape(mide_bs, edit=True,
                                target=(self.target_mode, num, temp_targetList[num], 1.0))
                # aliasAttr _jianbang_qaaa blendShape10.w[0]

                cmds.aliasAttr( target_nameList[num] ,mide_bs + ".w[{}]".format(num) )
                if obj_list[0]:
                    cmds.connectAttr(obj_list[0], obj_list[2].replace(self.BlendShapeNode, mide_bs))
                    cmds.connectAttr(obj_list[0], obj_list[2])
                else:
                    cmds.setAttr(obj_list[2], obj_list[3])
                if obj_list[1]:
                    cmds.setAttr(obj_list[2].replace(self.BlendShapeNode, mide_bs), l=True)


                    cmds.setAttr(obj_list[2], l=True)
            base_mode_skinNode = skinWeightUtils.skinTool.get_SkinNode(self.target_mode)
            if base_mode_skinNode:
                cmds.reorderDeformers(base_mode_skinNode,  mide_bs ,self.target_mode)

        cmds.delete("temp_copybsTool_grp_001")


class EditeBlednShapeTool(BlendShapeUtile.BlendShapeClass):

    def __init__(self ,mode):
        super(EditeBlednShapeTool ,self).__init__( mode)
        self.mode = mode

