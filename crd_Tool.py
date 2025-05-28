# coding=utf-8
import maya.cmds as cmds
import utils.rigging.arcUtils as arc

reload(arc)


def set_Constraint_grp():
    skin_joint_grp = "anim_skeletons_grp"
    Constraint_grp = "joint_Constraint_grp"
    modules_grp = "anim_modules_grp"

    obj_List = cmds.ls(skin_joint_grp, dag=1)

    typr_tool = arc.baseFunTool()

    for obj in obj_List:

        obj_type = typr_tool.check_objType(obj)

        if not cmds.objExists(Constraint_grp):
            cmds.createNode("transform", n=Constraint_grp)

        if obj_type == "parentConstraint" or obj_type == "scaleConstraint":
            cmds.parent(obj, Constraint_grp)

    cmds.parent(Constraint_grp, modules_grp)


def get_custom_attributes(node_name):
    """获取节点的所有自定义属性"""
    if not cmds.objExists(node_name):
        return []
    # 使用 listAttr 命令，设置 userDefined=True 只返回自定义属性
    custom_attrs = cmds.listAttr(node_name, userDefined=True) or []

    return custom_attrs


def lock_ctrl_attr():
    # 控制器与不解锁的属性
    ctrl_list = [u'mouth_R_dn_2_ctrl',
                 u'mouth_R_up_2_ctrl',
                 u'brow_R_all_ctrl',
                 u'brow_L_all_ctrl',
                 u'nose_R_nostril_ctrl',
                 u'nose_L_nostril_ctrl',
                 u'mouth_L_dn_2_ctrl',
                 u'mouth_L_up_2_ctrl',
                 u'mouth_R_1_ctrl',
                 u'mouth_L_1_ctrl',
                 u'face_R_malar_ctrl',
                 u'face_L_malar_ctrl',
                 u'jaw_M_open_ctrl',
                 u'eye_L_ball_ctrl',
                 u'eyelid_L_dn_all_ctrl',
                 u'eyelid_L_up_all_ctrl',
                 u'eye_R_ball_ctrl',
                 u'eyelid_R_dn_all_ctrl',
                 u'eyelid_R_up_all_ctrl']

    unLock_attr = ["sneer", "worry", "mad"]
    face_ctrl = cmds.ls(sl=1)
    for ctrl in ctrl_list:
        attr_List = get_custom_attributes(ctrl)
        for attr in attr_List:
            if attr not in unLock_attr:
                node_attr = ctrl + "." + attr
                cmds.setAttr(node_attr, l=True)


# 添加follow属性设置
import maya.cmds as  cmds


def FollowAttr(object, *args):
    # 约束切换链接的空组与物体之间的关系
    spaceGrp = object + "_drv"

    if not cmds.objExists(spaceGrp):
        cmds.group(object, n=object + "_drv")

    # 添加属性
    cmds.addAttr(object, longName="Follow", keyable=True, attributeType='enum', enumName=':'.join(args))

    for argNum, num in enumerate(args):

        # 添加空间切换的组
        if not cmds.objExists("zero_{}_space_grp".format(num)):
            print("createNode")
            # 添加loc
            loc = cmds.spaceLocator(name="Follow_{}_space_loc".format(num))[0]
            locGrp = cmds.group(loc, n='zero' + loc)

        else:
            loc = "Follow_{}_space_loc".format(num)
            locGrp = 'zero' + loc

    parConstraint = cmds.parentConstraint(loc, spaceGrp, maintainOffset=True)[0]
    # 鍒涘缓condition鑺傜偣锛屽苟灏哻ondition鑺傜偣鐨刼utColorR杩炴帴鍒皃arentConstraint鐨剋eight灞炴€т笂
    condition = cmds.createNode('condition', name=object + '_condition' + str(argNum))
    cmds.connectAttr(object + '.' + "Follow", condition + '.firstTerm')
    cmds.setAttr(condition + '.secondTerm', argNum)
    cmds.setAttr(condition + '.colorIfFalseR', 0)
    cmds.setAttr(condition + '.colorIfTrueR', 1)
    cmds.connectAttr(condition + '.outColorR', parConstraint + '.' + loc + 'W' + str(argNum))


args = ['World', 'head']
sel = cmds.ls(sl=1)
for ctrl in sel:
    FollowAttr(ctrl, *args)
