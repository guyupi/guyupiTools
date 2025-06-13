#!/usr/bin/env python
# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel


# 毛囊类，用于创建修改毛囊的各种操作
class Follicle(object):

    def __init__(self):
        pass

    def FromMatrixCreatefollicle(self, polyObject, valueU=0.5, valueV=0.5):
        """
        #传入的两个数值，分别是0-1范围内的数值，和一个字符串
        #输出两个字符串
        """
        # 声明一个字典，用来储存链接属性的名称
        connectAttrDic = {
            "in30": "result.position.positionX",
            "in31": "result.position.positionY",
            "in32": "result.position.positionZ",
            "in20": "result.normalizedNormal.normalizedNormalX",
            "in21": "result.normalizedNormal.normalizedNormalY",
            "in22": "result.normalizedNormal.normalizedNormalZ",
            "in10": "result.normalizedTangentV.normalizedTangentVX",
            "in11": "result.normalizedTangentV.normalizedTangentVY",
            "in12": "result.normalizedTangentV.normalizedTangentVZ",
            "in00": "result.normalizedTangentU.normalizedTangentUX",
            "in01": "result.normalizedTangentU.normalizedTangentUY",
            "in02": "result.normalizedTangentU.normalizedTangentUZ",

        }
        # 判断目标模型，是模型还是Surface曲面
        objShape = cmds.listRelatives(polyObject, s=1)[0]
        if cmds.objectType(objShape) == "nurbsSurface":

            # 创建出一个能存放loc的组
            if cmds.objExists("grp_Matrix_Follicle") is False:
                grp = cmds.createNode("transform", n="grp_Matrix_Follicle")

            # 创建loc节点
            locNode = cmds.createNode('locator')
            locTran = cmds.listRelatives(locNode, p=1)[0]
            cmds.parent(locTran, "grp_Matrix_Follicle")
            cmds.addAttr(locTran, ln="valueU", at="double", k=1, min=0, max=1, dv=0)
            cmds.addAttr(locTran, ln="valueV", at="double", k=1, min=0, max=1, dv=0)
            # 创造临时节点closepointOnSurface节点,与其他矩阵节点
            # temp_node = cmds.createNode("closestPointOnSurface")
            surfaceInfoNode = cmds.createNode("pointOnSurfaceInfo")
            fourMatrixNode = cmds.createNode("fourByFourMatrix")
            multMatrixNode = cmds.createNode("multMatrix")
            decomposeMatrixNode = cmds.createNode("decomposeMatrix")

            # 设置UV值，链接属性

            cmds.setAttr(locTran + ".valueU", valueU)
            cmds.setAttr(locTran + ".valueV", valueV)
            cmds.connectAttr(locTran + ".valueU", surfaceInfoNode + ".parameterU")
            cmds.connectAttr(locTran + ".valueV", surfaceInfoNode + ".parameterV")

            cmds.connectAttr(polyObject + '.worldSpace', surfaceInfoNode + '.inputSurface')

            # 矩阵部分相关链接设置
            for key, value in connectAttrDic.items():
                print key, value
                cmds.connectAttr(surfaceInfoNode + "." + value, fourMatrixNode + "." + key)

            cmds.connectAttr(multMatrixNode + ".matrixSum", decomposeMatrixNode + ".inputMatrix")
            cmds.connectAttr(fourMatrixNode + ".output", multMatrixNode + ".matrixIn[0]")
            cmds.connectAttr(locTran + ".parentInverseMatrix", multMatrixNode + ".matrixIn[1]")
            cmds.connectAttr(decomposeMatrixNode + ".outputTranslate", locTran + ".translate")
            cmds.connectAttr(decomposeMatrixNode + ".outputRotate", locTran + ".rotate")

            return surfaceInfoNode, locTran

        elif cmds.objectType(objShape) == "mesh":

            # 创建出一个能存放毛囊的组
            if cmds.objExists("grp_m_Follicle") is False:
                grp = cmds.createNode("transform", n="grp_m_Follicle")

            # 创建毛囊节点，获取毛囊节点的名称
            follicle_shape = cmds.createNode('follicle')
            follicle_tran = cmds.listRelatives(follicle_shape, p=1)[0]
            cmds.parent(follicle_tran, "grp_m_Follicle")

            cmds.connectAttr(objShape + '.outMesh', follicle_shape + '.inputMesh')

            cmds.connectAttr(objShape + '.worldMatrix[0]', follicle_shape + '.inputWorldMatrix')

            # 获取UV值closestPointOnMesh4.parameterU
            cmds.setAttr(follicle_shape + '.parameterU', valueU)
            cmds.setAttr(follicle_shape + '.parameterV', valueV)

            cmds.connectAttr(follicle_shape + '.outRotate', follicle_tran + '.rotate')
            cmds.connectAttr(follicle_shape + '.outTranslate', follicle_tran + '.translate')

            return follicle_tran

            # 根据物体的位置，给模型或曲面创建出毛囊

    def createFollicleForUV(self, direction, objList, creatNum=1):
        """
        #对输入的UV值进行批量添加毛囊
        :param direction: U,V
        :param objList: 模型的列表
        :param creatNum: 创建毛囊的数量
        :return:
        """
        if direction not in ["U", "V"]:
            cmds.warning("输入的方向错误！")
            return None


        if creatNum <= 0:
            return

        for num in range(0, creatNum ):

            if creatNum == 2:
                space = num
            elif creatNum > 2:
                if num == 0:
                    space = 0
                else:
                    space = (1.0 / (creatNum -1)) * num
            for obj in objList:

                if creatNum == 1:
                    self.FromMatrixCreatefollicle(obj ,0.5, 0.5)
                    continue

                if direction == "U":
                    ValueU = space
                    ValueV = 0.5
                else:
                    ValueU = 0.5
                    ValueV = space
                # print (space)
                self.FromMatrixCreatefollicle(obj, ValueU, ValueV)

    #
    #
    # ，obj为列表
    def fromObjCreateFollile(self, polyObject, objList):

        # 返回毛囊的所有名称
        FollileList = []
        for obj in list(objList):

            # 先判断模型是mesh还是Surface
            polyObjectShape = cmds.listRelatives(polyObject, s=1)[0]
            if cmds.objectType(polyObjectShape) == "mesh":

                # 创建pointonmesh节点,用来获取物体在模型上的UV值
                temp_node = cmds.createNode('closestPointOnMesh')
                cmds.connectAttr(polyObjectShape + '.worldMesh[0]', temp_node + '.inMesh')
                cmds.connectAttr(polyObjectShape + '.worldMatrix[0]', temp_node + '.inputMatrix')

            elif cmds.objectType(polyObjectShape) == "nurbsSurface":

                # 创建pointonmesh节点,用来获取物体在曲面上的UV值
                temp_node = cmds.createNode('closestPointOnSurface')
                cmds.connectAttr(polyObjectShape + '.worldSpace', temp_node + '.inputSurface')

            temp_loc = cmds.spaceLocator()[0]
            cmds.matchTransform(temp_loc ,obj ,pos = 1 ,rot = 1)
            cmds.connectAttr(temp_loc + '.translate', temp_node + '.inPosition')

            # 获取UV值
            value_U = cmds.getAttr(temp_node + '.parameterU')
            value_V = cmds.getAttr(temp_node + '.parameterV')

            # 创建毛囊
            FollileList.append(self.FromMatrixCreatefollicle(polyObject, value_U, value_V))

            cmds.delete(temp_loc ,temp_node)
        return FollileList

    # 选中物体创建铆钉（创建出面片与毛囊的结合体）
    # 原理是通过选中对角曲线放样出一个曲面，通过曲面来生成rive
    def fromObjEdgeCreateRivet(self, polyObject, EdgesA=1, EdgesB=2):

        # 创建出两个curveFromMeshEdge节点,loft节点，pointOnSurfaceInfo节点
        curveNodeA = cmds.createNode("curveFromMeshEdge")
        curveNodeB = cmds.createNode("curveFromMeshEdge")
        loftNode = cmds.createNode("loft")
        surfaceTemp = cmds.createNode("nurbsSurface")
        surfaceTempTran = cmds.listRelatives(surfaceTemp, p=1)[0]
        # 链接相关属性
        cmds.connectAttr(polyObject + ".worldMesh[0]", curveNodeA + ".inputMesh")
        cmds.connectAttr(polyObject + ".worldMesh[0]", curveNodeB + ".inputMesh")

        cmds.setAttr(curveNodeA + ".edgeIndex[0]", EdgesA)
        cmds.setAttr(curveNodeB + ".edgeIndex[0]", EdgesB)

        cmds.connectAttr(loftNode + ".outputSurface", surfaceTemp + ".create")

        follicleList = self.FromMatrixCreatefollicle(surfaceTempTran)

        cmds.setAttr(loftNode + ".uniform", 1)

        cmds.connectAttr(curveNodeA + ".outputCurve", loftNode + ".inputCurve[0]")
        cmds.connectAttr(curveNodeB + ".outputCurve", loftNode + ".inputCurve[1]")
        cmds.disconnectAttr(surfaceTemp + ".worldSpace[0]", follicleList[0] + ".inputSurface")
        # cmds.connectAttr(loftNode + ".outputSurface" , follicleList[0] + ".inputSurface")

        # cmds.delete(surfaceTempTran)

    def maodingFunc(self, objList):
        """
        传入物体列表，在每个物体对应的位置创建出铆钉
        """
        # 先创建出面片的集合体：
        meshList = []
        locList = []
        for obj in objList:
            meshTemp = cmds.polyPlane(w=1, h=1, sx=1, sy=1, ax=(1, 0, 0), ch=0)[0]
            cmds.matchTransform(meshTemp, obj, pos=1, rot=1)

            meshList.append(meshTemp)
        # 合并所有的面
        if len(meshList) > 1:
            meshEnd = cmds.polyUnite(meshList, ch=0)[0]
        else:
            meshEnd = meshList[0]
        # 展开mehs集合体的UV
        cmds.polyMultiLayoutUV(meshEnd + ".f[0:" + str(len(objList) - 1) + "]", lm=1, sc=1, rbf=1, fr=1, ps=0.2, l=2,
                               gu=1, gv=1, psc=0, su=1, sv=1)

        # 创建所有的毛囊
        follicleList = self.fromObjCreateFollile(meshEnd, objList)

        return follicleList

    # 判断模型是mesh，还是surface
    def meshOrSurface(self, polyObj):

        polyObjShape = cmds.listRelatives(polyObj, s=1)[0]

        if cmds.objectType(polyObjShape) == "mesh":
            return True

        elif cmds.objectType(polyObjShape) == "nurbsSurface":
            return False
        else:
            return None

