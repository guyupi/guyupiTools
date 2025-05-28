# coding=utf-8
#添加follow属性设置
import maya.cmds as  cmds

def FollowAttr(object, offset = True,  *args):
    # 约束切换链接的空组与物体之间的关系
    spaceGrp = object + "_drv"

    if not cmds.objExists(spaceGrp):
        cmds.group(object, n=object + "_drv")

    # 添加属性
    cmds.addAttr(object, longName="Follow", keyable=True, attributeType='enum', enumName=':'.join(args))

    for argNum, name in enumerate(args):

        # 添加空间切换的组
        if   cmds.objExists("zero_{}_space_grp".format(name)):

            # 添加loc
            loc = cmds.spaceLocator(name="Follow_{}_space_loc".format(name))[0]
            locGrp = cmds.group(loc, n='zero' + loc)

        else:
            loc = "Follow_{}_space_loc".format(name)
            locGrp = 'zero' + loc
        print locGrp
        parConstraint = cmds.parentConstraint(loc, spaceGrp, maintainOffset=offset)[0]

        # 鍒涘缓condition鑺傜偣锛屽苟灏哻ondition鑺傜偣鐨刼utColorR杩炴帴鍒皃arentConstraint鐨剋eight灞炴€т笂
        condition = cmds.createNode('condition', name=object + '_condition' + str(argNum))
        cmds.connectAttr(object + '.' + "Follow", condition + '.firstTerm')
        cmds.setAttr(condition + '.secondTerm', argNum)
        cmds.setAttr(condition + '.colorIfFalseR', 0)
        cmds.setAttr(condition + '.colorIfTrueR', 1)
        cmds.connectAttr(condition + '.outColorR', parConstraint + '.' + loc + 'W' + str(argNum))

def add_wuqi_left_right( offset = False):

    args = ['body', 'left_hand', 'right_hand']
    sel = cmds.ls(sl=1)
    for ctrl in sel:
        FollowAttr(ctrl, False , *args)

def add_belt_space_attr():

    # 添加follow属性设置
    args = ['Spine', 'Hip', 'Leg', 'World', 'Belt']
    sel = cmds.ls(sl=1)
    for ctrl in sel:
        FollowAttr(ctrl, True , *args)