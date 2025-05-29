# coding=utf-8
import os
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as cmds
import maya.mel as mel
import csv
import arcUtils as  arc

class base_Api():

    def get_MDependNode(self, name):
        u"""
        通过传入的名称来获取他的依赖节点
        :param name: 物体的名称
        :return: 依赖节点
        """
        if not cmds.objExists(name):
            raise Warning("%s:Object does not exist # " % name)

        selectionList = om.MSelectionList()
        selectionList.add(name)
        oNode = om.MObject()
        selectionList.getDependNode(0, oNode)
        return oNode

    def get_MPathByName(self, name):
        u"""
        通过传入的名称获取名称的长名称
        :param name: 名称
        :return: 模型的dagpath
        """
        if not cmds.objExists(name):
            raise Warning("%s:Object does not exist # " % name)

        selectionList = om.MSelectionList()
        selectionList.add(name)
        pathNode = om.MDagPath()
        selectionList.getDagPath(0, pathNode)
        return pathNode

    def transform_vtxId(self, vtx_array):
        """
        将maya默认的点的选择列表转化为点的序列编号
        :param vtx_array:
        :return: 点的编号列表
        """
        vtx_idArray = []
        for vtx_id in vtx_array:
            if ":" in vtx_id:
                star = int(vtx_id.split(":")[0].split("[")[1])
                end = int(vtx_id.split(":")[1].split("]")[0])
                vtx_idArray = vtx_idArray + list(range(star, end))
            else:
                vtx_idArray.append(int(vtx_id.split("[")[1].split("]")[0]))
        return vtx_idArray


class SkinWeight(base_Api):

    #创建绑定
    def build_bind(self, meshList, inf_jointList):
        # 建立绑定
        skinNodeList = []
        for mesh in meshList:
            cmds.skinCluster(inf_jointList, mesh,tsb=True)
            skinNode = self.get_SkinNode(mesh)
            skinNodeList.append(mesh)
        return skinNodeList

    #获取模型的蒙皮节点
    def get_SkinNode(self, mesh):
        # 获取模型的蒙皮节点
        try:
            skin = []
            om.MGlobal.executeCommand("findRelatedSkinCluster {}".format(mesh), skin)
            return skin[0]
        except:
            skinCls = None
        return skinCls

    #检查蒙皮节点，有的话就删除，没有就按照影响权重重新蒙皮
    def check_and_weights(self,mesh, inf_jnts):
        skin_name = self.get_SkinNode(mesh)

        if skin_name:
            cmds.skinCluster(e = 1,ub = 1)
        cmds.skinCluster(mesh, inf_jnts, tsb=1, mi=3,
                             bindMethod=0, skinMethod=0, lockWeights=False)

    #获取蒙皮节点的影响骨骼
    def get_infJointList(self, skinNode=None):
        # 获取蒙皮节点的影响骨骼列表
        jntS = None
        if skinNode:
            jntS = cmds.skinCluster(skinNode, query=True, influence=True)
        return jntS

    #对模型添加骨骼影响
    def add_infJoint(self, mesh, jointList):
        # 对蒙皮的对象添加新的骨骼影响
        skin_node = self.get_SkinNode(mesh)
        inf_jointList = self.get_infJointList(skin_node)
        if inf_jointList:
            add_jointList = [joint for joint in jointList if joint not in inf_jointList]
            if add_jointList:
                for joint in add_jointList:
                    cmds.skinCluster(skin_node, e=True, ai=joint, lw=True, wt=0)
            return add_jointList
        else:
            return

    #解锁所有骨骼
    def unhold_skin_joint_liw(self ,*args):
        for joint in args:
            cmds.setAttr(str(joint) + ".liw" ,0)


    #锁定所有骨骼
    def hold_skin_joint_liw(self ,*args):
        for joint in args:
            cmds.setAttr(str(joint) + ".liw" ,1)

    #移除未影响骨骼权重
    def remove_infJoint(self, mesh=None):
        # 移除没有权重的骨骼
        mel.eval("removeUnusedInfluences")

    #获取影响骨骼的位置属性
    def get_infJointTran(self, jointList=None):
        # 获取骨骼的transform的数值
        pos_array = []
        if jointList:
            pos_array = [cmds.xform(joint, q=True, ws=True, t=True) for joint in jointList]
        return pos_array

    #获取影响骨骼的旋转属性
    def get_infJointRot(self, jointList=None):
        # 获取骨骼的旋转的数值
        rot_array = []
        if jointList:
            rot_array = [cmds.xform(joint, q=True, ws=True, ro=True) for joint in jointList]

        return rot_array

    #获取影响骨骼的父对象属性
    def get_infParentArray(self, jointList=None):
        # 获取骨骼的父骨骼列表
        parent_array = []
        if jointList:

            for joint in jointList:
                parent = cmds.listRelatives(joint, parent=True)
                if parent:
                    parent_array.append(parent[0])

                else:
                    parent_array.append(None)
        return parent_array

    #获取超过四点权重的点的ID
    def get_fourinfJointPoint(self, mesh=None, weights=None, inf_jointMaxNum=4):
        """
        获取影响点受骨骼影响数大于inf_jointMaxNum的所有点序号
        :param mesh: 具有蒙皮的模型
        :param weights: 权重
        :return: 点的序号
        """
        skin_node = self.get_SkinNode(mesh)
        inf_len = len(self.get_infJointList(skin_node))
        if inf_len < inf_jointMaxNum:
            return None

        wei_len = len(weights)
        vtx_IdList = []
        for wei_id in range(0, wei_len, inf_len):
            inf_jointNum = 0
            for inf_id in weights[wei_id:wei_id + inf_len]:
                if inf_id > 0.0:
                    inf_jointNum += 1
                if inf_jointNum > inf_jointMaxNum:
                    vtx_IdList.append(wei_id / inf_len)
                    break

        return vtx_IdList

    #清理超过四点权重的点
    def clear_fourinfJointPoint(self, mesh=None, vtx_IdList=None, inf_jointMaxNum=4):
        """
        对点超过骨骼影响数的点进行清除
        :param mesh: 具有蒙皮信息的模型
        :param vtx_IdList: 超点的序号
        :param weights: 权重
        :param inf_jointMaxNum: 骨骼影响最大数
        :return:
        """
        inf_joint, weights = self.get_apiMeshSkinWeight(mesh, vtx_IdList)
        skin_node = self.get_SkinNode(mesh)
        inf_len = len(inf_joint)
        wei_len = len(weights)
        new_weight = []
        for wei_id in range(0, wei_len, inf_len):
            point_wei = weights[wei_id:wei_id + inf_len]
            sort_wei = point_wei.sort()[inf_jointMaxNum:]
            inf_wei = point_wei[0:inf_jointMaxNum]
            sum_wei = sum(sort_wei)
            # print sum_wei
        return vtx_IdList

    #获取模型与点的序号列表
    def get_vtxMobject(self, mesh=None, vtx_array=None):
        """
        将点的编号与mesh转换成MObject用于设置权重
        :param mesh: 模型
        :param vtx_array: 点的编号
        :return: mesh_dagPath, vertComp
        """
        mesh_dagPath = self.get_MPathByName(mesh)

        # 创建一个空的顶点组件对象
        vertComp = om.MObject()
        compFn = om.MFnSingleIndexedComponent()
        vertComp = compFn.create(om.MFn.kMeshVertComponent)

        if isinstance(vtx_array[0], str):
            vtx_array = self.transform_vtxId(vtx_array)
        elif isinstance(vtx_array[0], int):
            # 将点索引逐个添加到组件中
            for index in vtx_array:
                compFn.addElement(index)

        return mesh_dagPath, vertComp

    #通过api获取蒙皮权重
    def get_apiMeshSkinWeight(self, mesh=None, vtx_array=None, inf=None):

        # 获取一个模型的所有权重值
        if not vtx_array:
            vtx_array = cmds.ls('{}.vtx[*]'.format(mesh))

        Mmesh_dagPath, componentObj = self.get_vtxMobject(mesh, vtx_array)
        # 获取蒙皮相关的节点
        skinNode = self.get_SkinNode(mesh)
        mskin_Node = self.get_MDependNode(skinNode)

        # ...get mesh
        Mmesh_DagPath = self.get_MPathByName(mesh)

        # # ...get Vtx
        mfn_skinNode = oma.MFnSkinCluster(mskin_Node)

        weiDoubleArray = om.MDoubleArray()
        jointList = self.get_infJointList(skinNode)
        int_array = om.MIntArray()

        if inf:
            for i in inf:
                int_array.append(i)
        else:
            for i in range(len(jointList)):
                int_array.append(i)

        # ...getWeight
        mfn_skinNode.getWeights(Mmesh_DagPath, componentObj, int_array, weiDoubleArray)
        # weights_Array = np.array(list(dWeights), dtype='float64')
        # inf_Array = [dp.partialPathName() for dp in mfn_skinNode.influenceObjects()]

        return weiDoubleArray

    #通过api设置骨骼权重
    def set_apiMeshWeight(self, mesh=None,  weights=None, vtx_array=None ,inf = None):

        # 设置模型的所有权重值
        if vtx_array and not mesh:
            mesh = vtx_array[0].split(".")[0]
        elif mesh and not vtx_array:
            vtx_array = list(range(0, len(cmds.ls('{}.vtx[*]'.format(mesh), fl=1))))
        elif mesh and vtx_array:
            cmds.error(u"传入的模型和点信息有误")

        # 获取蒙皮节点

        mesh_skinNode = self.get_SkinNode(mesh)
        # if not mesh_skinNode:
        #     cmds.error(u"模型本身没有蒙皮信息")
        #     return

        self.add_infJoint(mesh ,inf)

        # 获取处理权重的类
        mSkin = self.get_MDependNode(mesh_skinNode)
        mfn_skin = oma.MFnSkinCluster(mSkin)

        # 获取影响骨骼数
        Mint_array = om.MIntArray()
        jointList = self.get_infJointList(mesh_skinNode)

        for i in range(len(jointList)):
            Mint_array.append(i)

        # 获取组件的类
        Mmesh_dagPath, mvtx_arry = self.get_vtxMobject(mesh, vtx_array)
        mfn_skin.setWeights(Mmesh_dagPath, mvtx_arry, Mint_array, weights)

    #导出骨骼权重
    def export_skinWeight(self, mesh=None, path="D:/work/data/weights/test.csw"):
        # 导出蒙皮权重
        # 获取蒙皮的相关信息
        skin_node = self.get_SkinNode(mesh)
        skin_weight = self.get_apiMeshSkinWeight(mesh=mesh ,vtx_array=None ,inf = None)
        inf_Array = self.get_infJointList(skin_node)
        inf_posArray = self.get_infJointTran(inf_Array)
        inf_rotArray = self.get_infJointRot(inf_Array)
        inf_parentArray = self.get_infParentArray(inf_Array)

        # print skin_node ,inf_Array ,inf_posArray ,inf_rotArray ,inf_parentArray ,skin_weight
        # 将蒙皮权重的信息写入某路径下的csw文档内
        with open(path, 'wb') as weightFile:
            w = csv.writer(weightFile, delimiter=' ', quoting=csv.QUOTE_NONE, escapechar=' ')
            w.writerow(["skinNode", ":", skin_node])
            w.writerow(['influence', ':', inf_Array])
            w.writerow(['influParent', ':', inf_parentArray])
            w.writerow(["inf_posArray :", inf_posArray])
            w.writerow(["inf_rotArray :", inf_rotArray])
            inf_jointlenght = len(inf_Array)
            for num in range(0, len(skin_weight), inf_jointlenght):
                vtx_id = num / inf_jointlenght
                new_wei = skin_weight[num: num + inf_jointlenght]

                # wirst_wei = ["{},{}".format(t,wei) for t ,wei in enumerate(new_wei) if wei != 0]

                # for t , wei in enumerate(new_wei):
                w.writerow(["{}:{}".format(vtx_id, new_wei)])

    #导入骨骼权重
    def import_skinweight(self, mesh, path="D:/work/data/weights/test.csw"):
        # 导入蒙皮权重
        # mesh_skinNode = self.get_SkinNode(mesh)

        with open(path, 'r') as weightFile:
            w = csv.writer(weightFile, delimiter=' ', quoting=csv.QUOTE_NONE, escapechar=' ')
            wei_data = weightFile.readlines()
            # wei_data.split("\r\n")
            skin_node = wei_data[0].split(": ")[1][:-2]
            inf_array = eval(wei_data[1].split(": ")[1])
            inf_parentArray = eval(wei_data[2].split(": ")[1][:-2])
            inf_pos = eval(wei_data[3].split(": ")[1][:-2])
            inf_rot = eval(wei_data[4].split(": ")[1][:-2])

            row = len(wei_data)

            weightList = om.MDoubleArray()
            for num in range(5, row):
                weight = eval(wei_data[num].split(":")[1][:-2])
                for wei in weight:
                    weightList.append(wei)

        self.check_and_weights(mesh , inf_array)

        self.set_apiMeshWeight(mesh = mesh , weights = weightList ,inf = inf_array)

    #对一个模型的两个骨骼权重数值的转移
    def transfer_jointZeroWeights(self, mesh, root_joint, from_joint):
        u"""
        :param mesh: 蒙皮模型
        :param root_joint: 目标骨骼
        :param from_joint: 编辑权重的骨骼
        :return:
        """
        # 获取模型的蒙皮影响骨骼
        skin_Node = self.get_SkinNode(mesh)
        inf_jointList = self.get_infJointList(skin_Node)
        cmds.setAttr("%s.maintainMaxInfluences" % skin_Node, False)

        # 判断from_joint ,root_joint是否在影响骨骼内,不在就添加影响
        add_jointList = []
        # 将添加的骨骼放到影响骨骼的总列表
        inf_jointList.extend(add_jointList)
        edit_jointList = [root_joint] + from_joint
        self.add_infJoint(mesh, edit_jointList)

        # 将影响骨骼锁定
        for joint in inf_jointList:
            liwAtr = "{}.liw".format(joint)
            if joint in edit_jointList:
                cmds.setAttr(liwAtr, False)
            else:
                cmds.setAttr(liwAtr, True)

        # 转移权重
        cmds.skinPercent(skin_Node, mesh, transformValue=[root_joint, 1.0])

    #对骨骼权重进行减法操作
    def subtract_jointWeights(self, mesh, allWeights, rootJoint, target_joint, target_weights ,Type = "-"):

        u"""
        分配骨骼权重的命令
        :param mesh: 蒙皮模型
        :param allWeights: 模型的所有权重
        :param rootJoint: 根骨骼
        :param target_joint: 分配的骨骼
        :param target_weights: 分配骨骼权重
        :return: weights
        """
        #获取mesh蒙皮的所有信息
        skin_node  = self.get_SkinNode(mesh)
        inf_jointList = self.get_infJointList(skin_node)
        rootjoint_num = inf_jointList.index(rootJoint)
        targetjoint_num = inf_jointList.index(target_joint)
        mesh_weights = self.get_apiMeshSkinWeight(mesh)

        #对权重进行加减操作
        new_weights = om.MDoubleArray()
        if Type == "-":

            allWeights_len = len(allWeights)
            infjoint_len = len(inf_jointList)
            vtx_num = allWeights_len/infjoint_len
            vtx_comp = []
            for num ,wei_num in enumerate(range(0,allWeights_len , infjoint_len)):
                # print num,wei_num
                #若两个任意一个的权重为0，那么就直接跳过
                if allWeights[wei_num + rootjoint_num] == 0 or target_weights[num] == 0:
                    continue

                #若root骨骼的权重比target_joint小，直接把root的骨骼权重赋值给target_joint
                #为了避免出现权重值为负数的情况
                if target_weights[num] >= allWeights[wei_num + rootjoint_num]:
                    allWeights[wei_num + targetjoint_num] = allWeights[wei_num + rootjoint_num]
                    allWeights[wei_num + rootjoint_num] = 0
                else:
                    allWeights[wei_num + rootjoint_num] = allWeights[wei_num + rootjoint_num] - target_weights[num]
                    allWeights[wei_num + targetjoint_num] = target_weights[num]
                    # print allWeights[wei_num + rootjoint_num] ,allWeights[wei_num + targetjoint_num]

                vtx_comp.append(num)

        return allWeights
        # self.set_apiMeshWeight(mesh ,vtx_comp ,allWeights )


    #重置绑定蒙皮
    def reset_skin_node(self ,*args):

        for mesh in args:
            mesh_skinNode = self.get_SkinNode(mesh)
            if mesh_skinNode:
                inf_skin = self.get_infJointList(mesh_skinNode)
                cmds.skinCluster(mesh_skinNode, edit=True, unbindKeepHistory=True)
                cmds.skinCluster(inf_skin, mesh)


    #maya权重操作的命令
    # 执行剪除小权重操作
    def prune_small_weights(self,mesh ,threshold=0.001):
        skinNode = self.get_SkinNode(mesh)
        inf_joint = self.get_infJointList(skinNode)
        self.unhold_skin_joint_liw(*inf_joint)
        mel.eval('doPruneSkinClusterWeightsArgList 1 { "' + str(threshold) + '" }')
        cmds.skinCluster(skinNode,e=1,fnw=1)

    # 执行标准化权重操作
    def normalize_weights(self ,*args):

        for mesh in args:
            skin_node = self.get_SkinNode(mesh)
            if skin_node:
                inf_skin = self.get_infJointList(skin_node)
                self.unhold_skin_joint_liw(*inf_skin)
                cmds.skinCluster(skin_node, e=1, fnw=1)


    # 执行移除未使用的蒙皮关节操作
    def remove_unused_skin_joints(self):
        mel.eval('removeUnusedInfluences')

    # 执行锤式权重方式
    def maya_hammer_wei(self ,*args):
        mel.eval("weightHammerVerts;")

    # 镜像权重+x-->-x
    def Mirror_Weight(self):
        str = " -mirrorMode YZ -surfaceAssociation closestPoint -influenceAssociation oneToOne -influenceAssociation closestJoint"
        mel.eval("doMirrorSkinWeightsArgList( 2, { \" " + str + " \" } );")

    # 镜像权重-x-->+x
    def Mirror_WeightRev(self):
        str = " -mirrorMode YZ -mirrorInverse -surfaceAssociation closestPoint -influenceAssociation oneToOne -influenceAssociation closestJoint"
        mel.eval("doMirrorSkinWeightsArgList( 2, { \" " + str + " \" } );")



class copySkinWeiTool(SkinWeight , arc.baseFunTool):

    def __init__(self):
        pass

    # objA是字符串类型，objB是一個模型或者一個模型的点的列表
    def CopySkin_OneToOne(self, objA, objB):




        # 查看objA有没有蒙皮节点
        ObjASkinName = self.get_SkinNode(objA)

        if ObjASkinName == "":
            cmds.warning(objA + " no have skinNode")
            return None
        # 获取A的骨骼影响数
        else:
            ObjAInfJoint = cmds.skinCluster(objA, q=True, inf=True)

        # 判断objB属于模型的点列表
        if ".vtx" in objB[0]:

            objBName = objB[0].split(".")[0]
            ObjBSkinName = self.get_SkinNode(objBName)
            # 判断objB是否存在蒙皮节点，若不存在直接复制权重即可
            if ObjBSkinName == "":
                cmds.skinCluster(objBName, ObjAInfJoint, tsb=True)
                cmds.copySkinWeights(objA, objBName, noMirror=True, surfaceAssociation="closestPoint",
                                     influenceAssociation="oneToOne")
                return True
            # 该列表的模型
            if ObjBSkinName != "":
                ObjBInfJoint = cmds.skinCluster(objBName, q=True, inf=True)

                difference_List = list(set(ObjAInfJoint) - set(ObjBInfJoint))

                jointList = []
                for joint in difference_List:
                    jointList.append(joint.name())

                if difference_List != "":
                    cmds.skinCluster(objBName, e=True, addInfluence=jointList, lockWeights=True, weight=0)

                cmds.select(objA, r=1)
                cmds.select(objB, add=1)
                mel.eval("CopySkinWeights;")

            else:

                cmds.skinCluster(objBName, ObjAInfJoint, tsb=True)
                cmds.copySkinWeights(objA, objBName, noMirror=True, surfaceAssociation="closestPoint",
                                     influenceAssociation="oneToOne")

        # 判断objB属于模型
        else:
            obj_type = self.check_objType(objB)

            newSkin = self.get_SkinNode(objB[0])
            if newSkin != "":
                cmds.delete(newSkin)

            cmds.skinCluster(objB[0], ObjAInfJoint, tsb=True)


            if obj_type == "mesh":


                cmds.copySkinWeights(objA, objB[0], noMirror=True, surfaceAssociation="closestPoint",
                                         influenceAssociation="oneToOne")

            elif obj_type == "nurbsSurface":

                newSkin = self.get_SkinNode(objB[0])
                vtx_poly = cmds.select(objA + '.vtx[0:]', r=1)
                vtx_srf = cmds.select(objB[0] + ".cv[0:][0:]", add=1)
                cmds.copySkinWeights(nm=1, sa='closestPoint', ia='closestJoint')






        return True

    def CopySkin_MoreToOne(self,*args):

        objAList = args[:-1]
        objB = args[-1]
        inf_jointlist = []

        #获取影响骨骼
        for obj in objAList:
            inf_jointlist.extend(self.get_infJointList(obj))
        #获取之后去除重复骨骼
        inflist = list(set(inf_jointlist))
        #获取目标模型是否有权重
        objB_skin = self.get_SkinNode(objB)
        if objB_skin:
            self.add_infJoint(objB, inflist)
            cmds.select(objAList)
            cmds.select(objB, add=1)
            try :
                mel.eval("copySkinWeights  -noMirror -surfaceAssociation closestPoint -influenceAssociation oneToOne -influenceAssociation closestJoint -influenceAssociation closestBone;")
            except:
                return
        else:
            self.build_bind([objB] , inflist)
            cmds.select(objAList)
            cmds.select(objB ,add = 1)
            #mel.eval( "copySkinWeightsCallback OptionBoxWindow|formLayout154|tabLayout12|formLayout156|tabLayout17|columnLayout109 1;")
            mel.eval("copySkinWeights  -noMirror -surfaceAssociation closestPoint -influenceAssociation oneToOne -influenceAssociation closestJoint -influenceAssociation closestBone;")

copySkinTool = copySkinWeiTool()
skinTool  = SkinWeight()

