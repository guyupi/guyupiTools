#!/usr/bin/env python
# -*- coding: utf-8 -*-
import maya.cmds as cmds
import arcUtils
reload(arcUtils)
class HierarchyNode(arcUtils.baseFunTool):

    def __init__(self ,path_node ):

        self.path_node = path_node
        self.node_shotName = self.get_node_shotName()
        self.parent_node = self.get_parent_node()
        self.uuid = self.get_uuid()
        self.node_type = self.get_node_type()


    def __eq__(self, other):
        if not isinstance(other, HierarchyNode):
            return False
        return (self.parent_node == other.parent_node  and self.node_shotName == other.node_shotName and self.node_type == other.node_type)


    def __hash__(self):

        parent_tuple = tuple(self.parent_node)

        return hash((parent_tuple, self.node_shotName, self.node_type))

    def get_parent_node(self):
        # 获取直接父节点（返回列表）
        return  cmds.listRelatives(self.path_node, parent=True) or []

    def get_node_shotName(self):
        return self.path_node.split("|")[-1]

    def get_uuid(self):
        return cmds.ls(self.path_node , uuid = 1)

    def get_node_type(self):
        long_name = cmds.ls(self.uuid , long = 1)
        return self.check_objType(long_name)


class checkList():
    def __init__(self , nodeA , nodeB):

        no_shape_nodeA_list ,no_shape_nodeB_list = self.manage_class(nodeA ,nodeB)
        self.HierarchyNodeA_List = [HierarchyNode(node) for node in no_shape_nodeA_list]
        self.HierarchyNodeB_List = [HierarchyNode(node) for node in no_shape_nodeB_list]


    def manage_class(self ,nodeA ,nodeB):
        nodeA_list = cmds.listRelatives(nodeA, allDescendents=True, fullPath=True) or []
        nodeB_list = cmds.listRelatives(nodeB, allDescendents=True, fullPath=True) or []
        no_shape_nodeA_list = [node for node in nodeA_list if not cmds.objectType(node) == 'shape']
        no_shape_nodeB_list = [node for node in nodeB_list if not cmds.objectType(node) == 'shape']
        return no_shape_nodeA_list ,no_shape_nodeB_list


    def check_HierarchyName(self):

        unEqualA_list = []
        unEqualB_list = []
        print (u"检查层级函数")
        if len(self.HierarchyNodeA_List) != len(self.HierarchyNodeB_List):
            print(u"两个层级下面的节点数量不同\n第一个层级下节点数量：{}   第二个层级下节点数量{}".format(len(self.HierarchyNodeA_List) ,len(self.HierarchyNodeB_List)))

        # for nodeA in self.HierarchyNodeB_List:
        #
        #     if nodeA not in self.HierarchyNodeB_List:
        #         unEqualA_list.append(nodeA)
        #
        # for nodeB in  self.HierarchyNodeA_List:
        #
        #     if nodeB not in self.HierarchyNodeA_List:
        #         unEqualB_list.append(nodeA)
        #
        # for node in unEqualA_list:
        #
        #     print u"第一个层级" ,node.node_shotName
        #
        # for node in unEqualB_list:
        #     print u"第二个层级", node.node_shotName
        diff = set(self.HierarchyNodeA_List).symmetric_difference(set(self.HierarchyNodeB_List))
        print(u"差异元素:", [obj.node_shotName for obj in diff])
