# /usr/bin/env python
# -*- coding: UTF-8 -*-
import maya.cmds as cmds
from maya.OpenMaya import *
from maya.OpenMayaAnim import *


class API_base(object):

    def __init__(self):
        pass

    # 获取选定物体
    def get_dagPathByName(self , name=""):
        """
        #获取物体的dag_path
        :return: 返回dag_path
        """
        selected = MSelectionList()
        dag_path = MDagPath()
        selected.add(name)
        selected.getDagPath(0, dag_path)
        return dag_path

    #获取依赖节点
    def get_dependNode(self, name):
        """
        通过名称获取依赖节点
        :param name: 物体名称或者，dag_path
        :return: 依赖节点类
        """
        selected = MSelectionList()
        dependNode = MObject()

        selected.add(name)
        if isinstance(name, list) and "." in name[0]:
            mesh = name[0].split(".")[0]
            components = MObject()
            mesh_dagpath = self.get_dagPathByName(mesh)
            selected.getDependNode(0, mesh_dagpath, name)
        else:
            selected.getDependNode(0, dependNode)
        return dependNode

    #获取模型的点信息
    def get_meshPoints(self , mesh='', py=False):
        dag_path = self.get_dagPathByName(mesh)
        fn_mesh = MFnMesh(dag_path)
        Mpoint = MPointArray()
        fn_mesh.getPoints(Mpoint)
        py_point = [[Mpoint[i][j] for j in range(3)] for i in range(Mpoint.length())]
        if py:
            return py_point
        else:
            return Mpoint

    #设置模型的点信息
    def set_meshPoint(self ,base_mesh, target_mesh):
        """
        #两个模型必须点数一致,将一个模型的形态，付给另一个模型
        :param base_mesh: 基本模型
        :param target_mesh: 目标模型
        :return:
        """

        base_meshPoints = self.get_meshPoints(base_mesh)
        target_meshDagPath = self.get_dagPathByName(target_mesh)
        target_mfnmesh = MFnMesh(target_meshDagPath)
        target_mfnmesh.setPoints(base_meshPoints)


    def set_scaleMeshPoints(self,mesh, scale):
        """
        将模型的
        :param mesh:
        :param scale:
        :return:
        """

        # mesh_points = get_meshPoints(mesh)
        # mesh_dagPath = get_dagPathByName(mesh)
        # mfnMesh = MFnMesh(mesh_dagPath)
        # for i in range(mesh_points.length()):
        #     mesh_points.set(mesh_points[i] * scale , i)
        # mfnMesh.setPoints()
        pass

    #获取模型
    def get_meshSkinweight(self,mesh="", component=[]):
        if mesh != "" and component == []:
            component = [mesh + ".vtx[*]"]
        elif mesh == "" and component != []:
            mesh = component[0].split(".")[0]
        elif mesh == "" and component == []:
            return

        # 获取相关的数据类型

        # 获取mesh的dagpath
        Mesh_dagPath = self.get_dagPathByName(mesh)

        # 获取蒙皮节点
        skins = []
        MGlobal.executeCommand("findRelatedSkinCluster " + Mesh_dagPath.fullPathName(), skins)
        if len(skins) == 0:
            MGlobal.displayError("{}不具有蒙皮节点，请检查后".format(Mesh_dagPath.fullPathName()))
            return
        skin_cluster = skins[0]

        # 获取蒙皮骨骼列表
        skin_node = self.get_dependNode(skin_cluster)
        mfn_skin_node = MFnSkinCluster(skin_node)
        joint_dagpaths = MDagPathArray()
        mfn_skin_node.influenceObjects(joint_dagpaths)
        inf_Arry = []
        for i in range(joint_dagpaths.length()):
            inf_Arry.append(joint_dagpaths[i].fullPathName().split("|")[-1])

        # 获取权重
        selected = MSelectionList()
        mcomponent = MObject()
        selected.add(Mesh_dagPath.fullPathName() + ".vtx[*]")
        selected.getDagPath(0, Mesh_dagPath, mcomponent)
        influenceIndices = MIntArray()
        for i in range(joint_dagpaths.length()):
            influenceIndices.append(i)
        weights = MDoubleArray()
        mfn_skin_node.getWeights(Mesh_dagPath, mcomponent, influenceIndices, weights)

        # for i in range(weights.length()):
        #     print weights[i]

        return skin_cluster, inf_Arry, weights

    #通过权重拆分bs
    def split_meshByWei(self,base_mesh, skin_mesh):
        # 先获取两个模型的点，以及skin_mesh上的权重信息
        base_mesh_points = self.get_meshPoints(base_mesh, False)
        skin_mesh_points = self.get_meshPoints(skin_mesh, False)
        skir_node, inf_Arry, weights = self.get_meshSkinweight(skin_mesh)
        # print "meshA points :" ,meshA_points
        # print "meshB points :", meshB_points
        # print "skir_node is :", skir_node
        # print "inf_Arry is :", inf_Arry
        # print "weight is :", weight
        # 获取两个模型之间的偏移向量
        offsets = MVectorArray()
        offsets.setLength(base_mesh_points.length())
        for i in range(base_mesh_points.length()):
            offsets.set(base_mesh_points[i] - skin_mesh_points[i], i)

        # 复制出新的模型，给新的模型，设置拆分后的形态
        for joint_id in range(len(inf_Arry)):
            new_mesh = []
            MGlobal.executeCommand("duplicate " + skin_mesh, new_mesh)
            new_mesh_dagPath = self.get_dagPathByName(new_mesh[0])
            # print new_mesh[0]
            new_mfnmesh = MFnMesh(new_mesh_dagPath)
            split_points = MPointArray()
            split_points.setLength(skin_mesh_points.length())
            for vtx_id in range(skin_mesh_points.length()):
                split_points.set(skin_mesh_points[vtx_id] + offsets[vtx_id] * weights[vtx_id * len(inf_Arry) + joint_id],
                                 vtx_id)
            new_mfnmesh.setPoints(split_points)


    def BS_subtraction(self, pose_mesh, subt_mesh, base_mesh):
        # 先获取两个模型的点，以及skin_mesh上的权重信息
        pose_mesh_points = self.get_meshPoints(pose_mesh, False)
        subt_mesh_points = self.get_meshPoints(subt_mesh, False)
        base_mesh_points = self.get_meshPoints(base_mesh, False)

        # 获取两个模型之间的偏移向量
        offsets = MVectorArray()
        offsets.setLength(base_mesh_points.length())
        for i in range(base_mesh_points.length()):
            offsets.set(pose_mesh_points[i] - subt_mesh_points[i], i)

        new_mesh = []
        MGlobal.executeCommand("duplicate " + base_mesh, new_mesh)
        new_mesh_dagPath = self.get_dagPathByName(new_mesh[0])

        new_mfnmesh = MFnMesh(new_mesh_dagPath)
        reve_points = MPointArray()
        reve_points.setLength(base_mesh_points.length())

        for vtx_id in range(base_mesh_points.length()):
            reve_points.set(base_mesh_points[vtx_id] + offsets[vtx_id], vtx_id)

        new_mfnmesh.setPoints(reve_points)


    def is_selected_object_a_mesh(self):
        """
        判断选中的物体是否为模型（多边形网格）
        :return: 如果选中物体是模型返回True，否则返回False
        """
        # 获取当前选中的物体列表
        selection_list = MSelectionList()
        MGlobal.getActiveSelectionList(selection_list)

        # 检查是否有选中的物体
        if selection_list.length() == 0:
            MGlobal.displayWarning("没有选中任何物体。")
            return False

        # 获取第一个选中物体的DAG路径
        dag_path = MDagPath()
        selection_list.getDagPath(0, dag_path)

        # 检查该物体是否为多边形网格
        return dag_path.hasFn(MFn.kMesh)


    def get_shape_node_name(self, node_name):
        """
        获取物体的形状节点名称，如果没有则返回 False
        :param node_name: 物体的名称
        :return: 形状节点名称或 False
        """
        dag_path = self.get_dagPathByName(node_name)
        shape_dag_path = MDagPath(dag_path)
        try:
            shape_dag_path.extendToShape()
            return shape_dag_path.fullPathName()
        except:
            return False


    def check_node_type(self,name):
        dag_path = self.get_dagPathByName(name)
        depend_node = self.get_dependNode(name)

        shape = self.get_shape_node_name(name)

        if shape:
            if dag_path.hasFn(MFn.kNurbsCurve):
                return "曲线"
            elif dag_path.hasFn(MFn.kJoint):
                return "骨骼"
            elif dag_path.hasFn(MFn.kFollicle):
                return "毛囊"
            elif dag_path.hasFn(MFn.kLocator):
                return "locator"
            elif dag_path.hasFn(MFn.kNurbsSurface):
                return "nurbs"
            elif dag_path.hasFn(MFn.kIkHandle):
                return "ikHandle"
            elif depend_node.hasFn(MFn.kConstraint):
                return "约束"
            else:
                return name



        elif dag_path.hasFn(MFn.kTransform):
            return "transform节点"

