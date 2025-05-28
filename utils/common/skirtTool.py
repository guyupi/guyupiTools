# /usr/bin/env python
# -*- coding: UTF-8 -*-
import maya.cmds as cmds
import pymel.core as pm
from ..rigging import jointUtils
from ..rigging import commonsUtile
from ..rigging import control

reload(jointUtils)
reload(control)


class skirCommon(object):

    def __init__(self, skirtName):
        self.skirt = skirtName
        self.temp_grp = self.skirt + "Temp_riging_grp"
        self.hide_grp = self.skirt + "Temp_hide_grp"
        self.joint_grp = self.skirt + "Temp_joint_grp"
        self.ctrl_grp = self.skirt + "Temp_ctrl_grp"
        self.loc_grp = self.skirt + "Temp_loc_grp"
        self.curve_grp = self.skirt + "Temp_curve_grp"
        self.up_curve = self.skirt + "_upCurve_001"
        self.down_curve = self.skirt + "_downCurve_001"
        self.up_loc = "dirloc_" + self.up_curve
        self.down_loc = "dirloc_" + self.down_curve
        self.up_locList = []
        self.down_locList = []

    def create_Frame(self, spans=8):

        cmds.createNode("transform", n=self.temp_grp)
        cmds.createNode("transform", n=self.hide_grp, p=self.temp_grp)
        cmds.createNode("transform", n=self.loc_grp, p=self.temp_grp)
        cmds.setAttr(self.hide_grp + ".visibility", 0)
        self.create_SkirtFrame(spans=spans)

    # 创建Skir曲线
    def create_SkirtCurve(self, spans=8):
        # 创建两个曲线
        if spans <= 4:
            return
        nr = [0, 1, 0]
        cmds.createNode("transform", n=self.curve_grp)
        cmds.parent(self.curve_grp, self.temp_grp)
        skirt_upCurve = cmds.circle(s=spans, nr=nr, ch=0, r=3.5, n=self.up_curve)[0]
        cmds.move(0, 10, 0, self.up_curve, absolute=True)
        skirt_downCurve = cmds.circle(s=spans, nr=nr, ch=0, r=5, n=self.down_curve)[0]
        cmds.parent(skirt_downCurve, skirt_upCurve)
        cmds.parent(skirt_upCurve, self.curve_grp)
        return [skirt_upCurve, skirt_downCurve]

    def create_SkirtFrame(self, spans=8):
        # 构建框架
        skirtCurve = self.create_SkirtCurve(spans)
        up_locgrp, up_locList = commonsUtile.createLocForCurve(skirtCurve[0])
        down_locgrp, down_locList = commonsUtile.createLocForCurve(skirtCurve[1])

        # 给曲线上添加显示loc的开关
        attr = ["lov_vis", "joint_vis"]
        cmds.addAttr(skirtCurve[0], shortName=attr[0], attributeType='bool', keyable=True)
        cmds.connectAttr(skirtCurve[0] + "." + attr[0], up_locgrp + ".visibility")
        cmds.addAttr(skirtCurve[1], shortName=attr[1], attributeType='bool', keyable=True)
        cmds.connectAttr(skirtCurve[1] + "." + attr[1], down_locgrp + ".visibility")

        cmds.parent(up_locgrp, down_locgrp, self.temp_grp)

        # 在创建出一个始终在曲线中间的loc，用与确定骨骼方向
        up_directionLoc = cmds.spaceLocator(n="dirloc_{}".format(skirtCurve[0]))[0]
        down_directionLoc = cmds.spaceLocator(n="dirloc_{}".format(skirtCurve[1]))[0]

        # 用loc列表对这个中间的loc做约束
        cmds.pointConstraint(up_locList, up_directionLoc, mo=False, weight=1)
        cmds.pointConstraint(down_locList, down_directionLoc, mo=False, weight=1)
        cmds.parent(up_directionLoc, down_directionLoc, self.hide_grp)
        cmds.setAttr(self.hide_grp + ".visibility", 0)
        self.up_locList = up_locList
        self.down_locList = down_locList

    def create_JointCon(self, midJointNum=5):
        # 创建承载着骨骼还有控制器的组
        cmds.createNode("transform", n=self.joint_grp)
        cmds.createNode("transform", n=self.ctrl_grp)
        # 通过目标约束来改变上loc的方向
        for jointList_num, (locUp, locDown) in enumerate(zip(self.up_locList, self.down_locList)):
            # aimConstraint -offset 0 0 0 -weight 1 -aimVector 1 0 0 -upVector 0 -1 0 -worldUpType "object" -worldUpObject dirloc_skirt_upCurve_001;
            cmds.aimConstraint(locDown, locUp, weight=1, aimVector=(1, 0, 0), upVector=(0, -1, 0), worldUpType="object",
                               worldUpObject=self.up_loc)

            # 在对应loc的位置创建首尾骨骼，并插入骨骼
            up_Joint = cmds.createNode("joint", p=locUp)
            down_joint = cmds.createNode("joint", p=locDown)
            cmds.matchTransform(down_joint, up_Joint, rot=True)
            cmds.parent(down_joint, up_Joint)
            cmds.makeIdentity(down_joint, apply=True, r=1)

            # 创建骨骼
            midjoint = jointUtils.jointCla.create_MidJoint([up_Joint, down_joint], midJointNum)
            # cmds.parentConstraint(locUp ,up_Joint ,weight=1)
            cmds.parent(up_Joint, self.joint_grp)

            # 创建控制器
            jointList = [up_Joint] + midjoint + [down_joint]
            # print "create joint is " , jointList
            new_jointList = []
            space = commonsUtile.get_worldSpaceToLF(up_Joint)
            for num, joint in enumerate(jointList):
                cmds.rename(joint, "jnt_{}_{}{}_{:03}".format(space, self.skirt, chr(65 + jointList_num), num + 1))
                new_jointList.append("jnt_{}_{}{}_{:03}".format(space, self.skirt, chr(65 + jointList_num), num + 1))

            control.ControlClass.createFKIKCon(objList=new_jointList, cvShape="PlaneD", IKciji=True, endCon=False,
                                               dirveType="yueshu")
            cmds.parent("zero_ctrl_{}_{}{}_{:03}".format(space, self.skirt, chr(65 + jointList_num), 1), self.ctrl_grp)

    def create_jianmo(self):
        # 创建骨骼用来确定曲线复制后位移的方向
        cmds.parent(self.down_curve, w=True)
        up_jointJm = cmds.createNode("joint")
        cmds.matchTransform(up_jointJm, self.up_loc, pos=1)
        down_jointJm = cmds.createNode("joint")
        cmds.matchTransform(down_jointJm, self.down_loc, pos=1)
        cmds.parent(up_jointJm, down_jointJm)
        cmds.joint(down_jointJm, e=True, zso=True, oj='xyz')
        # 获取骨骼的tx值可以得到正确的方向
        upjoint_tx = cmds.getAttr(up_jointJm + ".tx")
        # 复制出来曲线并移动它
        temp_curve = cmds.duplicate(self.up_curve, n="up_" + self.up_curve)[0]

        cmds.parent(temp_curve, up_jointJm)
        cmds.setAttr(up_jointJm + '.tx', upjoint_tx * 1.2)
        cmds.parent(self.down_curve, self.curve_grp)
        cmds.parent(temp_curve, self.curve_grp)
        # 放样出模型
        jm_mode = cmds.loft(temp_curve, self.up_curve, self.down_curve, ch=1, po=1, rsn=True)[0]
        # 反转法线
        cmds.polyNormal(jm_mode, normalMode=0, userNormalMode=0, ch=1)
        cmds.delete(up_jointJm, down_jointJm)
