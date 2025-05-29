# /usr/bin/env python
# -*- coding: UTF-8 -*-
from maya import cmds

class Dynamic(object):

    def __init__(self):

        self.nucleus = ""
        self.hairSys = {
            "hairSysTra" : "",
            "hairSysShape" : "",
            "hairSysList" : []
        }
        self.hairSysNum = 0
        self.FollicleList = []


    def createHairSys(self , className, nucleus=None):
        """
        create hair system
        :param className: str, prefix_name of the original joint chain
        :param nucleus: str, whether specified nucleus
        :return: dict, {'hair_shape': hairShape, 'hairTransNode': hairTransNode}
        """

        nucleus = nucleus or createNucleus(className=className)
        # hair System
        hairShape = cmds.createNode('hairSystem', n=className + '_hairSysShape')
        hairTransNode = cmds.listRelatives(hairShape, p=1, c=0, s=0)[0]
        hairTransNode = cmds.rename(hairTransNode, className + '_hairSysNode_#')
        hairShape = cmds.listRelatives(hairTransNode, c=1, p=0, s=1)[0]
        cmds.select(cl=1)

        # connectAttr
        cmds.connectAttr('time1.outTime', hairShape + '.currentTime', f=1)
        index = cmds.getAttr(nucleus + '.inputActive', size=1)
        inputActive = '%s.inputActive[%s]' % (nucleus, index)
        inputStart = '%s.inputActiveStart[%s]' % (nucleus, index)
        output_object = '%s.outputObjects[%s]' % (nucleus, index)

        cmds.setAttr(hairShape + '.active', 1)

        cmds.connectAttr(hairShape + '.currentState', inputActive, f=1)
        cmds.connectAttr(hairShape + '.startState', inputStart, f=1)
        cmds.connectAttr(nucleus + '.startFrame', hairShape + '.startFrame', f=1)
        cmds.connectAttr(output_object, hairShape + '.nextState', f=1)

        # add hair attr
        if not cmds.attributeQuery('hair', node=hairShape, exists=1):
            cmds.addAttr(hairShape, longName='hair', at='message', multi=1)

        # add nucleus attr
        if not cmds.attributeQuery('nucleus', node=nucleus, exists=1):
            cmds.addAttr(nucleus, longName='nucleus', at='message', multi=1)

        self.hairSys.hairSysTra = hairTransNode
        self.hairSys.hairSysTra = hairShape
        self.hairSys.hairSysList.append(hairTransNode)

        return {'hairShape': hairShape,
                'hairTransNode': hairTransNode,
                'nucleus': nucleus}

    def createNucleus(self , className):
        """
        create nucleus
        :param jointList: 类名
        :return: nucleus：立场名称
        """

        nucleus = cmds.createNode('nucleus', n=className + '_nucleus_#')
        cmds.connectAttr('time1.outTime', nucleus + '.currentTime', f=1)

        # 添加属性
        if not cmds.attributeQuery('nucleus', node=nucleus, exists=1):
            cmds.addAttr(nucleus, longName='nucleus', at='message', multi=1)
        #修改立场名称
        self.nucleus = nucleus
        return nucleus

    def createFollicle(self,FollicleName):
        """
        创建出毛囊
        :param FollicleName: 毛囊名称
        :return: 返回列表
        """
        if not  cmds.objExists("Dynamic_noMove_grp_001"):
            cmds.createNode("transform",n = "Dynamic_noMove_grp_001")
        folshapeName = cmds.createNode("follicle", name=FollicleName + "shape")
        folName = cmds.listRelatives(folshapeName, p=1)[0]
        cmds.parent(folName , "Dynamic_noMove_grp_001")

        return [folName,folshapeName]

    def addFollicleToHairSys(self , hairSysName , follicleName ,cvName):
        """
        创建毛囊添加到动力学系统中
        :param hairSysName: str:毛囊的系统名称
        :param follicleName:str: 毛囊的名字
        :param cvName: string:输入曲线的名称
        :return: string:返回输出曲线
        """
        #创建毛囊
        addFollicle = self.createFollicle(follicleName)
        cvShape = cmds.listRelatives(cvName, s = 1)[0]
        hairSysShapeName = cmds.listRelatives(hairSysName , s = 1)[0]
        #链接相关属性
        cmds.connectAttr(cvShape + ".local" , addFollicle[1] + ".startPosition")
        #disconnectAttr curve1rebuiltCurveShape1.local follicleShape1.startPosition;
        #disconnectAttr hairSystemShape1.outputHair[0] follicleShape1.currentPosition;

        cmds.connectAttr(hairSysShapeName + ".")
