#!/usr/bin/env python
# -*- coding: utf-8 -*-

from maya import cmds
import maya.mel as mel
import maya.api.OpenMaya as om2
import skinWeightUtils
from ...UI.uiClass.mayaPrint import printTool
from commonsUtile import get_sceneSizeforMesh
reload(skinWeightUtils)

class boneJoint():

    def __init__(self):
        pass

    # 对选定的对象创建单个骨骼
    def createJointForPoly(self, poly, skin=False):
        """
        通过创建簇生成骨骼
        :param poly: 传入的模型
        :param skin: 是否绑定蒙皮
        :return: 骨骼（string）
        """
        # 创建簇
        cluster = cmds.cluster(poly)
        # 在簇的位置创建骨骼
        joint = cmds.joint(None)
        cmds.matchTransform(joint, cluster, pos=1, rot=1)
        # 可选：删除簇的显示形状节点，只保留变换节点
        cmds.delete(cluster)

        if isinstance(poly ,unicode):

            if "." not in poly and skin:
                cmds.skinCluster(poly, joint)

        elif isinstance(poly ,list):
            for obj in poly:
                if "." not in obj and skin:
                    cmds.skinCluster(obj, joint)
        return joint

    # 对选定的每个对象都创建骨骼
    def createJointsForPoly(self, polyList, skin=False):
        """
        根据选顶对象批量创建骨骼
        :param polyList: 选中的模型列表
        :return: 骨骼列表
        """
        jointList = []
        for poly in polyList:

            joint = self.createJointForPoly(poly, skin)
            jointList.append(joint)
        return jointList

    #判断曲线与创建骨骼链的数量
    def check_curve_jointNum(self,curveList ,jointNum ,equidistance=False):


        if jointNum < 2:
            printTool.mayaError(u"输入的骨骼数量不能小于2!!")
            return

        cv_jointNum = []
        cv_lenList = []
        curveList_jointnum_Dictionary = {}
        if equidistance:

            if len(curveList) < 2 :
                printTool.mayaError(u"在等距模式下，曲线的数量要大于2!!")
                return

            for cv in curveList:
                sv_shape = cmds.listRelatives(cv, s=1)[0]
                curve_info = cmds.createNode("curveInfo")
                cmds.connectAttr(sv_shape + ".worldSpace", curve_info + ".inputCurve")
                cv_len = cmds.getAttr(curve_info + ".arcLength")
                cv_lenList.append(cv_len)
                cmds.delete(curve_info)
            max_value = max(cv_lenList)
            for cv_len ,curve_name in zip(cv_lenList, curveList):
                joints = (cv_len / max_value) * jointNum
                joints = max(1, joints)

                curveList_jointnum_Dictionary[curve_name] = int(round(joints))
        else:
            for curve_name in curveList:
                curveList_jointnum_Dictionary[curve_name] = jointNum

        return curveList_jointnum_Dictionary


    #通过一个骨骼位置获取曲线的
    def get_curve_parameter_at_joint(self ,curve_name, joint_name):
        """
        通过骨骼位置获取曲线上对应位置的参数值

        参数:
        - curve_name: 曲线名称
        - joint_name: 骨骼名称

        返回:
        - 参数值 (float)
        """
        # 获取骨骼的世界位置
        joint_pos = cmds.xform(joint_name, query=True, worldSpace=True, translation=True)
        joint_point = om2.MPoint(joint_pos[0], joint_pos[1], joint_pos[2])

        # 获取曲线的 DAG 路径
        selection = om2.MSelectionList()
        selection.add(curve_name)
        curve_dag = selection.getDagPath(0)

        # 创建曲线函数集
        curve_fn = om2.MFnNurbsCurve(curve_dag)

        # 计算曲线上离骨骼最近的点的参数值
        param = curve_fn.closestPoint(
            joint_point,
            tolerance=1e-6,
            space=om2.MSpace.kWorld
        )

        # 验证参数值是否有效
        min_param, max_param = curve_fn.knotDomain
        if param < min_param:
            param = min_param
        elif param > max_param:
            param = max_param

        return param

    # def create_curveToJoint(self, curve , jointNum, equidistance=False):
    #
    #     cv_jointNum = []
    #     cv_lenList = []
    #     if equidistance:
    #
    #         if len(curve) < 2:
    #             return
    #
    #         for cv in curve:
    #             sv_shape = cmds.listRelatives(cv, s=1)[0]
    #             curve_info = cmds.createNode("curveInfo")
    #             cmds.connectAttr(sv_shape + ".worldSpace", curve_info + ".inputCurve")
    #             cv_len = cmds.getAttr(curve_info + ".arcLength")
    #             cv_lenList.append(cv_len)
    #             cmds.delete(curve_info)
    #         max_value = max(cv_lenList)
    #         for cv_len in (cv_lenList):
    #             joints = (cv_len / max_value) * jointNum
    #             joints = max(1, joints)
    #             cv_jointNum.append(int(round(joints)))
    #     else:
    #         for num in range(len(curve)):
    #             cv_jointNum.append(jointNum)
    #
    #
    #     for cv, joints_Num in zip(curve, cv_jointNum):
    #
    #         jointList = []
    #         for num in range(joints_Num + 1):
    #             # 第一个骨骼
    #             joint = cmds.createNode('joint')
    #
    #             pathNode = cmds.pathAnimation(joint, fractionMode=True, follow=True, worldUpVector=[0, 1, 0],
    #                                           followAxis='x', upAxis='y', c=cv)
    #             cmds.delete(pathNode + '.uValue', inputConnectionsAndNodes=1)
    #             # 设置U值
    #             cmds.setAttr(pathNode + '.uValue', (1.0 / joints_Num) * num)
    #             # 删除路径动画
    #             cmds.delete(mp=True)
    #             jointList.append(joint)
    #             # 设置层级关系
    #             if num == 0:
    #                 firstJoint = joint
    #                 parentJoint = firstJoint
    #             else:
    #                 cmds.parent(joint, parentJoint)
    #                 parentJoint = joint
    #
    #             cmds.makeIdentity(joint, apply=True, r=1)
    #         #
    #
    #         cmds.joint(jointList[0], e=1, oj='xyz', sao='yup', zso=True,ch = True)
    #     # return jointList

    def create_curveToJoint(self, curve , jointNum, equidistance=False):

        dic = self.check_curve_jointNum(curve , jointNum, equidistance)

        if dic == None:
            return

        cv_jointlist_dic = {}

        for cv, joints_Num in dic.items():

            cv_jointlist_dic[cv] = []

            # curve_points = cmds.getAttr(cv + ".spans") + cmds.getAttr(cv + ".degree")
            #
            # curve_point = cv + ".cv[{}]".format(str(curve_points- 1))
            # joint_end = self.createJointForPoly(curve_point , skin = False)
            #
            # curve_parameter = self.get_curve_parameter_at_joint(cv , joint_end)
            #
            # cmds.delete(joint_end)
            # for joint in range(jointNum + 1):
            #     parameter = curve_parameter * ( joint *1.0 / jointNum *1.0)
            #     print curve_parameter ,parameter , joint , jointNum
            #     position = cmds. pointOnCurve(cv , pr = parameter)
            #
            #     jointList.append(cmds.joint(p = position))
            #
            #
            # cmds.makeIdentity(jointList[0], apply=True, r=1)
            #
            #
            # cmds.joint(jointList[0], e=1, oj='xyz', sao='yup', zso=True,ch = True)

            for num in range(joints_Num + 1):
                # 第一个骨骼
                joint = cmds.createNode('joint')

                pathNode = cmds.pathAnimation(joint, fractionMode=True, follow=True, worldUpVector=[0, 1, 0],
                                              followAxis='x', upAxis='y', c=cv)

                cmds.delete(pathNode + '.uValue', inputConnectionsAndNodes=1)
                # 设置U值
                cmds.setAttr(pathNode + '.uValue', (1.0 / joints_Num) * num)


                # 删除路径动画
                cmds.select(joint)
                mel.eval("DeleteMotionPaths;")
                cv_jointlist_dic[cv].append(joint)
                # 设置层级关系
                if num == 0:
                    firstJoint = joint
                    parentJoint = firstJoint
                else:
                    cmds.parent(joint, parentJoint)
                    parentJoint = joint

                self.set_joint_orient(cv_jointlist_dic[cv][0])
                self.setJintOrientZero(cv_jointlist_dic[cv][-1])

        return cv_jointlist_dic


    def create_MidJoint(self, jointList, midNum=1):

        """
        # 对两段骨骼创建的中间创建中间骨骼
        :param jointList: 输入骨骼列表
        :param midNum: 插入的骨骼数量
        :return: 骨骼列表
        """
        midJointList = []
        if len(jointList) == 1:
            jointList = cmds.ls(jointList, dag=1, type="joint")

        if len(jointList) < 2 or midNum == 0:
            return []

        for joint_num in range(len(jointList) - 1):
            firstJoint = jointList[joint_num]
            # 获得首个骨骼的位置信息，新建一个临时的首位骨骼，并放到传入首位骨骼的位置
            firstJoint_Space = cmds.xform(firstJoint, query=True, translation=True, worldSpace=True)
            jointTempFirst = cmds.joint(firstJoint)
            # cmds.matchTransform(jointTempFirst, firstJoint, rot=1)

            # 获得第二个骨骼的位置信息，新建一个临时的第二骨骼，放到第二个骨骼的位置
            jointListchildren = cmds.listRelatives(firstJoint, children=True)[0]
            jointListchildren_Space = cmds.xform(jointListchildren, query=True, translation=True, worldSpace=True)
            jointTempSecond = cmds.joint(p=jointListchildren_Space)
            cmds.xform(jointTempSecond, translation=jointListchildren_Space, worldSpace=True)

            # 修改层级
            # cmds.parent(jointTempSecond, jointTempFirst)
            cmds.parent(jointTempFirst, w=True)

            # 获取第二个骨骼的tx属性
            jointTempSecond_tx = cmds.getAttr(jointTempSecond + '.tx')

            # # 循环创建中间骨骼，并修改层级关系，设置tx属性
            parentJoint = jointTempFirst
            for num in range(midNum):

                # jointTx是每段骨骼的距离
                jointTx = jointTempSecond_tx / (midNum + 1)
                # 插入关节
                midJoint = cmds.insertJoint(parentJoint)

                # 将骨骼放到对应的位置
                cmds.setAttr(midJoint + '.tx', jointTx)
                midJointList.append(midJoint)


            cmds.parent(midJointList[-1], firstJoint)

            cmds.parent(jointListchildren, midJointList[joint_num * midNum] )
            print jointListchildren ,midJointList[-1]
            cmds.delete(jointTempFirst, jointTempSecond)
            # print jointListchildren,midJointList[-1 * midNum]
            # if joint_num == len(jointList) - 2 :
            #     cmds.parent(jointListchildren, midJointList[-1 * midNum])
            # midJointList.reverse()
            print midJointList , jointListchildren

        return midJointList

    # 删除末端骨骼
    def deleteEndJoint(self):
        pass

    # 确认关节方向
    def set_joint_orient(self ,*args):
        for joint in args:
            self.makeIdentity_joint(joint)
            cmds.joint(
                joint,
                edit=True,
                orientJoint='xyz',
                secondaryAxisOrient='yup',
                children=True,
                zeroScaleOrient=True
            )

    # 输入关节列表
    def setJintOrientZero(self, *args):
        orient = ['.jointOrientX', '.jointOrientY', '.jointOrientZ']
        for num in range(len(args)):
            for ori in orient:
                cmds.setAttr(args[num] + ori)



    # 输入骨骼列表（list），状态（int）
    def visOrientPiv(self, *jointList):
        """
        # 将骨骼列表下的所有骨骼显示切换局部旋转轴
        :param jointList: 骨骼链
        :return:
        """
        mel.eval("ToggleLocalRotationAxes")

    def jointReverse(self, jointList):
        """
        将骨骼链反转过来（方法二，创建IK，然后将IK曲线反转）
        :param jointList:
        :return:
        """
        if len(jointList) <= 1:
            cmds.error("请至少选择两个骨骼！")
            return
        cmds.parent(jointList, w=1)
        firstJointParent = cmds.listRelatives(jointList[0], p=1)
        for i in range(len(jointList) - 1):
            cmds.parent(jointList[i], jointList[i + 1])

        cmds.joint(jointList[len(jointList) - 1], edit=True, orientJoint='xyz', secondaryAxisOrient='xup',
                   children=True, zeroScaleOrient=True)

        self.setJintOrientZero(jointList[len(jointList) - 1])
        if firstJointParent:
            cmds.parent(jointList[len(jointList) - 1], firstJointParent[0])

    # 创建splineIK
    def createSplineIK(self, jointList, prefixName, curve=None):
        """
        创建SplineIK
        :param jointList: 骨骼列表
        :param curve: str, 前缀名称
        :return: list(str), IK_Handle = [ikh, effector, crv]
        """
        if not curve:
            # create IK Spline
            IK_Handle = cmds.ikHandle(n=prefixName + '_ikh', sj=jointList[0],
                                      ee=jointList[-1], sol='ikSplineSolver', scv=0, pcv=0)
            IK_Handle[-1] = cmds.rename(IK_Handle[-1], prefixName + '_Crv_Input')

            # add input curve attr
            if not cmds.attributeQuery('inputCurve', node=IK_Handle[-1], exists=1):
                cmds.addAttr(IK_Handle[-1], longName='inputCurve', at='message')

        else:
            # add jointList to exists curve
            IK_Handle = cmds.ikHandle(n=prefixName + '_ikh', sj=jointList[0], ee=jointList[-1],
                                      sol='ikSplineSolver', c=curve, ccv=0, roc=0, pcv=0, snc=1)
            IK_Handle.append(curve)

        # add IK handle attr
        if not cmds.attributeQuery('IKHandle', node=IK_Handle[0], exists=1):
            cmds.addAttr(IK_Handle[0], longName='IKHandle', at='message')

        return IK_Handle


    def dis_rotation(self):
        u"""
        显示切换物体的局部坐标信息
        :return:
        """
        mel.eval("ToggleLocalRotationAxes")

    def select_hisJoint(self ,sel):
        u"""
        选择层级下的所有骨骼
        :param sel:
        :return:
        """
        all_hisJointList = []
        for obj in sel:
            objList = cmds.ls(obj ,dag = 1 ,type = "joint")
            all_hisJointList += objList

        cmds.select(all_hisJointList)
        return all_hisJointList

    def select_skin_jointList(self ,meshList):
        u"""
        选中物体蒙皮的所有骨骼
        :param meshList:
        :return:
        """
        all_skin_joint = []
        for mesh in meshList:
            jointList = skinWeightUtils.skinTool.get_infJointList(mesh)
            all_skin_joint += jointList

        cmds.select(all_skin_joint)
        return all_skin_joint

    def change_jointSize(self ,num):
        u"""
        改变骨骼的大小显示效果
        :param num:
        :return:
        """
        mel.eval("jointDisplayScale {};".format(num))


    def mirrorJoint(self ,joint ,  leve , type , old_string ,new_string ):

        u"""
        骨骼镜像操作
        :param joint:
        :param leve:
        :param type:
        :param old_string:
        :param new_string:
        :return:
        """

        if leve == 0:
            cmds.mirrorJoint(joint, mirrorXY=True, mirrorBehavior=type, searchReplace=(old_string, new_string))

        elif leve == 1:
            cmds.mirrorJoint(joint, mirrorYZ=True, mirrorBehavior=type, searchReplace=(old_string, new_string))

        else:
            cmds.mirrorJoint(joint, mirrorXY=True, mirrorBehavior=type, searchReplace=(old_string, new_string))


    def Batch_mirrorJoint(self  ,jointList ,  leve , type , old_string ,new_string ):
        u"""
        骨骼批量镜像
        :param jointList:
        :param leve:
        :param type:
        :param old_string:
        :param new_string:
        :return:
        """
        for joint in jointList:
            self.mirrorJoint(joint ,  leve , type , old_string ,new_string )



    def create_loc(self,objList, size):
        u"""
        确定骨骼方向的loc预设
        :param objList:
        :param size:
        :return:
        """
        for obj in objList:

            if cmds.objectType(obj) != "joint":
                return

            if not cmds.objExists("temp_setOrient_{}_grp".format(obj)):
                loc_grp = cmds.createNode("transform", n="temp_setOrient_{}_grp".format(obj))
                loc = cmds.spaceLocator(n="temp_setOrient_" + obj)[0]

            cmds.parent(loc, loc_grp)

            hight = size / 10
            cmds.setAttr(loc + ".localScaleY", hight)
            cmds.setAttr(loc + ".localScaleX", hight / 2.0)
            cmds.setAttr(loc + ".localScaleZ", hight / 2.0)
            cmds.setAttr(loc + ".localPositionY", hight)

            cmds.setAttr(loc + '.tx', lock=True, k=False, cb=False)
            cmds.setAttr(loc + '.ty', lock=True, k=False, cb=False)
            cmds.setAttr(loc + '.tz', lock=True, k=False, cb=False)

            # cmds.setAttr(loc + '.rx' ,lock = True ,k = False ,cb = False)
            cmds.setAttr(loc + '.ry', lock=True, k=False, cb=False)
            cmds.setAttr(loc + '.rz', lock=True, k=False, cb=False)

            cmds.setAttr(loc + '.sx', lock=True, k=False, cb=False)
            cmds.setAttr(loc + '.sy', lock=True, k=False, cb=False)
            cmds.setAttr(loc + '.sz', lock=True, k=False, cb=False)
            cmds.matchTransform(loc_grp, obj, pos=1, rot=1)

    def change_jointRotate(self):
        u"""
        对骨骼预设方向的loc确定对应骨骼链的方向
        :return:
        """
        loc_grp_list = cmds.ls("temp_setOrient_*_grp")

        for loc_grp in loc_grp_list:

            loc = cmds.listRelatives(loc_grp, children=True)[0]
            head_joint = cmds.ls(loc_grp.split("_setOrient_")[1].split("_grp")[0])[0]

            join_list = cmds.ls(head_joint, dag=1)

            cmds.makeIdentity(head_joint, a=1, r=1, pn=1, n=0)

            cmds.parent(join_list[1:], w=1)

            cmds.matchTransform(head_joint, loc, pos=1, rot=1)

            parent_joint = head_joint

            for joint in join_list[1:]:
                cmds.parent(joint, parent_joint)

                cmds.setAttr(joint + ".jointOrientX", 0)

                parent_joint = joint

            cmds.setAttr(join_list[-1] + ".jointOrientY", 0)
            cmds.setAttr(join_list[-1] + ".jointOrientZ", 0)

        cmds.delete(loc_grp_list)

    def makeIdentity_joint(self , joint):
        cmds.select(joint )
        try:
            cmds.makeIdentity(a=1, r=1, s=1, n=0, pn=1)
        except:
            printTool.mayaError(u"骨骼被链接，或者与模型有蒙皮，不能冻结属性")



jointCla = boneJoint()
