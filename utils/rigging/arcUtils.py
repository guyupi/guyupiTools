#!/usr/bin/env python
# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel
import string
import time
import functools
import re

class baseFunTool(object):

    def __init__(self):
        pass

    #获取obj的形状节点
    def get_shape(self,object_name):
        try:
            # 获取物体的形状节点
            shape_nodes = cmds.listRelatives(object_name, shapes=True)[0]

            if shape_nodes:
                return shape_nodes
            else:
                return None
        except:
            return None

    #判断物体是属于什么类型的节点
    def check_objType(self, obj):

        obj_shape = self.get_shape(obj)
        if obj_shape:

            type = cmds.nodeType(obj_shape)
            return type
        else:
            type = cmds.nodeType(obj)
            return type

    #获取他的父对象
    def get_parent_node(self ,object_name):
        try:
            # 获取节点的父对象
            parent = cmds.listRelatives(object_name, parent=True)
            if parent:
                return parent[0]
            else:
                return None
        except Exception as e:
            print "发生错误:{}".format(e)
            return None

    #获取节点的历史输入历史
    def get_inputs_node(self ,object_name):
        obj_shape = self.get_shape(object_name)
        if obj_shape:

            type = cmds.nodeType(obj_shape)
            return type
        else:
            type = cmds.nodeType(object_name)
            return type

# 筛选所需要的节点
class Filter(baseFunTool):

    def __init__(self , Type , rev):
        """
        :param Type: #type是从获取的所有内容里面获取对应的节点信息
        :param rev: 是否反选类型之外的所有节点
        """
        self.type = Type
        self.reve = rev

    def GetFilter(self,obj_List):
        """
        筛选想要的节点
        """
        FilterList = []
        node_list = []

        for obj in obj_List:
            if "." not in obj  and obj not in node_list:
                node_list.append(obj)


        for node in node_list:
            if self.check_objType(obj) == "mesh":
                FilterList.append(node)

        return FilterList


    def ListToDic(self, objList):
        # 选中物体包括点，线面,转化为字典
        objNamedic = {}
        # objNameArray = ()
        for num in range(len(objList)):
            if '.' in objList[num]:
                midObj = objList[num].split(".")

                if midObj[0] not in objNamedic:
                    objNamedic[midObj[0]] = [objList[num]]
                else:
                    objNamedic[midObj[0]].append(objList[num])
            else:
                objNamedic[objList[num]] = [objList[num]]
                # print midObj
        return objNamedic

    #将字典转化为列表
    def dicToList(self, objNamedic):
        objList = []
        for key in objNamedic.keys():
            temp = []

            if objNamedic[key] == None:
                objList.append(key)
                continue

            for value in objNamedic[key]:
                objName = key + "." + str(value)
                temp.append(objName)
                # print type(value)

            objList.append(temp)

        return objList

    def toList(self, objList):
        # 选中物体包括点，线面,转化为字典
        objNameList = []
        temp = []
        for num in range(len(objList)):
            row = 0
            if '.' in objList[num]:
                midObj = objList[num].split(".")

                if midObj[0] in objNameList[row][0]:
                    objNameList[row].append(objList[num])

                else:
                    objNameList.append([objList[num]])
                    row += 1
                    print type(midObj[0]), type(objNameList[row][0])
            else:
                objNameList.append([objList[num]])
                row += 1
                # print midObj
        return objNameList





def get_shape(node, intermediate=False, full_path=True):

    if cmds.nodeType(node) in ['transform', 'joint']:
        if full_path:
            shapes = cmds.listRelatives(node, shapes=True, path=True, f=True)
        else:
            shapes = cmds.listRelatives(node, shapes=True, path=True)
        if not shapes:
            shapes = []
        for shape in shapes:
            is_intermediate = cmds.getAttr("{}.intermediateObject".format(shape))
            if intermediate and is_intermediate and cmds.listConnections(shape, source=False):
                # 通常我们只保留被连接的中间形节点
                return shape
            elif not intermediate and not is_intermediate:
                return shape
            else:
                return shapes[0]
        # if shapes:
        #     return shapes[0]
    elif cmds.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface', 'lattice']:
        if full_path:
            parent_nod = cmds.listRelatives(node, parent=True, f=True)[0]  # component mode
        else:
            parent_nod = cmds.listRelatives(node, parent=True)[0]  # component mode
        if cmds.nodeType(parent_nod) in ['mesh', 'nurbsCurve', 'nurbsSurface', 'lattice']:
            return parent_nod
        return node
    elif cmds.nodeType(node) in ['follicle', 'camera', 'clusterHandle']:
        return node
    return None


class GetFilter(object):
    """
    将所有选择的物体转换为需要的物体列表，
    比如选了关节，模型，模型点，  但我要获取模型列表，那就将模型点转为模型，并把关节过滤掉，将模型转为列表返回
    """
    def __init__(self, filter_type='mesh', inputObjs=None, noWarning=False):
        self.__inputObjs = inputObjs
        self.__filterObjs = []
        self.__filterType = filter_type
        self.__noWarning=noWarning
        # self.init()
        pass
    @property
    def filterObjs(self):
        return self.__filterObjs

    def __enter__(self):

        if self.__inputObjs is None:
            all_objs = cmds.ls(sl=1, fl=1)
        else:
            all_objs = self.__inputObjs
        element_objs = []
        transform_objs = []

        for obj in all_objs:
            if '.' in obj:
                element_objs.append(obj)
            else:
                transform_objs.append(obj)
        all_objs_filter = element_objs+transform_objs
        if all_objs_filter:

            all_dag_objs = list(set([x.split('.')[0] for x in all_objs_filter]))
            self.__filterObjs = []
            if self.__filterType == 'mesh':

                for dag in all_dag_objs:
                    shp = get_shape(dag)
                    if shp:
                        if cmds.objectType(shp) == 'mesh':
                            self.__filterObjs.append(dag)
            elif self.__filterType == 'mesh_vtx':

                if element_objs:
                    nod = list(set([x.split('.')[0] for x in element_objs]))

                    for n in nod:
                        n_shp = get_shape(n)

                        if cmds.objectType(n_shp) == 'mesh':
                            n_elements = []
                            for ele in element_objs:
                                if ele.split('.')[0] == n:
                                    n_elements.append(ele)
                            cmds.select(n_elements, r=True)
                            cmds.ConvertSelectionToVertices()
                            self.__filterObjs += cmds.ls(sl=True, fl=True)

            elif self.__filterType == 'joint':

                lis = []
                for dag in all_dag_objs:
                    if cmds.objectType(dag) == 'joint':
                        lis.append(dag)
                self.__filterObjs += lis

            elif self.__filterType == 'transform':
                lis = []
                for dag in all_dag_objs:
                    if cmds.objectType(dag) == 'transform':
                        lis.append(dag)
                self.__filterObjs += lis

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # print(self.__filterObjs)
        if not self.__filterObjs and not self.__noWarning:
            cmds.warning('no type({}) selected!!!'.format(self.__filterType))
        pass


def convert_flattenVtxs_toLis(vtxs):
    cmds.select(vtxs, r=True)
    lis = cmds.ls(sl=True)
    return lis


def get_meshes_vtxs(exclusive=True):
    # get current select mesh and set to item
    mesh = []
    with GetFilter('mesh', noWarning=True) as GetSl:
        mesh = GetSl.filterObjs
    mesh_vtxs = []
    with GetFilter('mesh_vtx', noWarning=True) as GetSl:
        mesh_vtxs = GetSl.filterObjs

    if not mesh and not mesh_vtxs:
        cmds.warning(u'请至少选择一个模型或者点')
    if mesh:
        mesh = list(set(mesh))
    if mesh_vtxs:
        mesh_vtxs = list(set(mesh_vtxs))

    if mesh and mesh_vtxs and exclusive:
        return mesh_vtxs
    else:
        return mesh+mesh_vtxs


def return_result(printStr):
    mel.eval("print \"\\n\";")
    mel.eval("print \"// Result: {} //\"".format(printStr))


def get_parent_array(array):
    if not isinstance(array, list):
        return cmds.warning('only array supported')
    aa = []
    for a in array:
        if not cmds.objExists(a):
            return cmds.warning('a obj not exist or duplicated')
        parent = cmds.listRelatives(a, p=True)
        if parent:
            pp = parent[0]
        else:
            pp = ''
        aa.append(pp)
    return aa


def return_list(obj=None):
    """
    将进入的obj，string或者list转换为list输出
    Args:
        obj(str, list):

    Returns:

    """
    lis = []
    if obj:
        if isinstance(obj, (str, unicode)):
            lis.append(obj)
        elif isinstance(obj, list):
            lis = obj
        elif isinstance(obj, tuple):
            lis = list(obj)
    return lis


def get_obj_type(obj):
    lis = return_list(obj)
    obj_type_dic = {}
    if lis:
        for ob in lis:
            shape = get_shape(ob)

            if not shape:
                nod_type = cmds.objectType(ob)

                export_type = 'grp'
                if nod_type == 'transform':
                    if 'offset' in ob.lower():
                        export_type = 'offset'
                    elif 'reverse' in ob.lower():
                        export_type = 'rvs'
                elif nod_type == 'joint':
                    export_type = 'jnt'
                elif nod_type == 'ikHandle':
                    export_type = 'ikHand'
            else:
                nod_type = cmds.objectType(shape)
                export_type = 'ctrl'
                if nod_type == 'mesh':
                    export_type = 'mesh'
                elif nod_type == 'locator':
                    export_type = 'loc'

            obj_type_dic.update({ob: export_type})
    return obj_type_dic


def get_str_part_and_num(obj):
    des = obj.rstrip(string.digits)

    des_num = len(des)
    index = obj[des_num:]
    if not index:
        index = 1
    return des, index


class Naming(object):
    """
    目前正常支持两种命名格式：一是adv命名格式 比如 FKSpine1_M
                            二是自己固有的命名格式 new_m_test_001
                            三是带有标签的命名格式 todo

    """
    def __init__(self, name=None, node_type=None, side=None, resolution=None, description=None, index=None,
                 compose_mod='custom', descriptionSuffix=''):
        self.__name = name
        self.__type = node_type
        self.__side = side
        self.__resolution = resolution
        self.__description = description
        # self.__tag = tag
        self.__index = index
        self.__composeMod = compose_mod

        self._endParts = ''
        self.__sideAll = ['l', 'm', 'r', 'L', 'M', 'R']
        # for get mirror
        self.__composeType = None
        self.__prime = None
        # ... add by 2022.10.24
        self.__descriptionSuffix = descriptionSuffix
        self.__composeSet = True  # True for Auto , False for handle
        self.__composeMethod = self.__composeMod
        self.typeDic = ['zero', 'jnt', 'driven', 'space', 'connect']
        #
        if self.__name:
            self.decompose()

    @property
    def composeMethod(self):
        return self.__composeMethod

    @property
    def composeSet(self):
        return self.__composeSet

    @composeSet.setter
    def composeSet(self, value):
        self.__composeSet = value

    @property
    def descriptionSuffix(self):
        return self.__descriptionSuffix

    @descriptionSuffix.setter
    def descriptionSuffix(self, value):
        self.__descriptionSuffix = value

    @property
    def end(self):
        return self._endParts

    @end.setter
    def end(self, value):
        self._endParts = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    # @property
    # def tag(self):
    #     return self.__tag
    #
    # @type.setter
    # def type(self, value):
    #     self.__tag = value

    @property
    def side(self):
        return self.__side

    @side.setter
    def side(self, value):
        self.__side = value

    @property
    def resolution(self):
        return self.__resolution

    @resolution.setter
    def resolution(self, value):
        self.resolution = value

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, value):
        self.__index = value

    @property
    def name(self):
        self.compose()
        return self.__name + self._endParts

    def get_name_by_type(self, typeStr):
        self.type = typeStr
        self.compose()
        return self.name

    def get_mirror(self):

        if self.__prime is not None:
            if self.__prime.endswith('_R'):
                return self.__prime.replace('_R', '_L')
            elif self.__prime.endswith('_L'):
                return self.__prime.replace('_L', '_R')
            else:
                return self.__prime
        else:
            self.side = self.get_mirror_side(self.side)
            return self.name

    @staticmethod
    def get_mirror_side(side):
        out = 'm'
        if side == 'l':
            out = 'r'
        elif side == 'r':
            out = 'l'
        elif side == 'R':
            out = 'L'
        elif side == 'L':
            out = 'R'
        return out

    def compose(self):
        name_parts = []
        if self.__name is not None:
            name_parts = self.__name.rpartition("_")
        self.__name = ''
        adv_flag = False

        if self.__composeMod == "adv":
            adv_flag = True
        else:
            if name_parts:
                if name_parts[-1] in self.__sideAll:
                    adv_flag = True

        if adv_flag:
            self.adv_compose()
        else:
            self.custom_compose()

    def decompose(self):

        if self.__name.endswith('End'):
            self._endParts = 'End'
            self.__name = self.__name[:-3]

        name_parts = self.__name.split("_")

        if len(name_parts) > 5 or len(name_parts) < 4:
            self.__prime = self.__name
            self.adv_decompose()
            self.__composeMethod = 'adv'

        else:
            if name_parts[1] not in self.__sideAll:
                self.__prime = self.__name
                self.adv_decompose()

            self.custom_decompose()

    def custom_compose(self):
        for name_part in [self.__type, self.__side, self.__resolution, self.__description]:
            if name_part:
                self.__name += name_part + "_"
        self.__name = "{}{:03d}".format(self.__name, int(self.__index)) + self._endParts

    def custom_decompose(self):
        name_parts = self.__name.split("_")

        if len(name_parts) != 4 and len(name_parts) != 5:

            self.__type = name_parts[0]
            self.__side = 'm'
            self.__description = "test"
            self.index = 1
        else:
            self.__type = name_parts[0]
            self.__side = name_parts[1]
            if len(name_parts) == 5:
                self.__resolution = name_parts[2]
            else:
                self.__resolution = None
            self.__description = name_parts[-2]
            self.__index = name_parts[-1]

    def adv_compose(self):
        if self.__index is not None:
            self.__description = '{}{}'.format(self.__description[0].upper(), self.__description[1:])
            self.__name = "{}{}_{}".format(self.__description, int(self.__index), self.__side.upper())
        else:
            self.__name = "{}_{}".format(self.__description, self.__side)

    def adv_decompose(self):
        nod_type_dic = get_obj_type(self.__name)
        node_type = nod_type_dic.get(self.__name)

        self.__type = node_type

        name_parts = self.__name.split('_')
        while '' in name_parts:
            name_parts.remove('')
        self.__side = 'm'
        if name_parts[-1] in self.__sideAll:
            self.__side = name_parts[-1].lower()
        if cmds.objExists(self.__prime):
            pos = cmds.xform(self.__prime, q=1, ws=1, t=1)
            if pos[0] < 0:
                self.__side = 'r'
            elif pos[0] > 0:
                self.__side = 'l'
        self.__description = name_parts[0].rstrip(string.digits)

        if self.__descriptionSuffix:
            if self.__descriptionSuffix in self.__description:
                self.__type = self.__description.rpartition(self.__descriptionSuffix)[-1]
                self.__description = self.__description.rpartition(self.__descriptionSuffix)[0]

        des_num = len(self.__description)
        index = name_parts[0][des_num:]

        self.__index = 1

        if index:
            self.__index = int(index)
        self.__name = '{}_{}_{}_{}'.format(self.__type, self.__side, self.__description, self.__index)

    def mirror(self):
        if self.__side == "l":
            self.__side = 'r'
        elif self.__side == 'r':
            self.__side = 'l'
        elif self.__side == 'L':
            self.__side = 'R'
        elif self.__side == 'R':
            self.__side = 'L'

    def get_new(self):
        """
        if 'ctrl_r_MouthSecA_004' exists -- > return 'ctrl_r_MouthSecB_004' ....
        if 'ctrl_r_MouthSec_004' exists -- > return 'ctrl_r_MouthSecA_004' ....
        Returns:

        """
        i = 0

        des = self.description
        if self.__name:
            if self.__name.endswith('End'):
                self.__name = self.__name[:-3]

        name_part = des
        if self.__descriptionSuffix:
            if self.__descriptionSuffix in des:
                name_part = des.rpartition(self.__descriptionSuffix)[0]
        self.__name = '{}_{}_{}_{:03d}'.format(self.__type, self.__side, name_part+self.__descriptionSuffix, i+1)

        while cmds.objExists(self.__name) and i < 100:
            i += 1

            description = name_part + self.__descriptionSuffix

            self.__name = '{}_{}_{}_{:03d}'.format(self.__type, self.__side, description, i)

        return self.__name

    def get_new_name(self):

        if self.__composeSet:

            #  这里的目的是：如果自动设置模式，则将组合名字方式设置为adv命名方式，否则设置为默认命名格式
            self.__composeMod = self.__composeMethod

        if self.__composeMod == 'custom':
            return self.get_new()
        else:
            return self.get_adv_new()

    def get_adv_new(self):
        i = 0

        des = self.description
        if self.__descriptionSuffix:
            if self.__descriptionSuffix in des:
                des = des.rpartition(self.__descriptionSuffix)[0]
        mid_num = ""
        if i != 0:
            mid_num = str(i)
        name = des + self.__descriptionSuffix + self.__type.title() + mid_num + '_{}'.format(self.__side.upper())

        while cmds.objExists(name) and i < 100:
            i += 1

            name_split = name.rpartition('_')[0]
            if self.__descriptionSuffix:
                name_split = name_split.rpartition(self.__descriptionSuffix)[0]
            part, num = get_str_part_and_num(name_split)

            name = part + self.__descriptionSuffix + self.__type.title() + str(i) + '_{}'.format(self.__side.upper())

        return name

    def get_index_new(self):
        i = 0

        if self.__name:
            if self.__name.endswith('End'):
                self.__name = self.__name[:-3]

        while cmds.objExists(self.name) and i < 100:
            i += 1
            self.__index += 1
            self.compose()
        return self.__name

    def get_prime_new(self):
        return_name = None
        if self.__prime:
            parts = self.__prime.split('_')

            while '' in parts:
                parts.remove('')
            while 'prefix' in parts:
                parts.remove('prefix')
            if len(parts) > 3:
                return cmds.warning('current can not handle')
            side = ''
            for attr in ['_M', '_L', '_R']:
                if self.__prime.endswith(attr):
                    side = attr
                    break

            if len(parts) < 3:
                name_prefix = parts[0]

                name = name_prefix

                i = 0

                while cmds.objExists(name) and i < 100:
                    i += 1
                    name = name_prefix + str(i)
                return_name = name + side
                #

        return return_name


def joints_name_preHandle(joints):
    """
    对关节名进行预处理，比如从max转到maya的关节可能会存在FBXASC032 意义为空格 我希望将空格转为"_"输出
    Args:
        joints:

    Returns:

    """
    jnts_new = []
    if joints:
        jnts_new = [x.replace('FBXASC032', '_') for x in joints]
    return jnts_new


def filter_side_from_str(text):
    pattern_priority = ['_L_', '_l_', '_R_', '_r_',
                        'L_', 'l_', 'R_', 'r_',
                        '_L', '_l''_r', '_r']
    batch = None
    for pattern in pattern_priority:
        if re.search(pattern, text):
            text = re.sub(pattern, '', text)
            batch = [pattern, text]
            break
    return batch




class UndoFunc(object):
    def __enter__(self):
        cmds.undoInfo(openChunk=True)

    def __exit__(self, *exc_info):
        cmds.undoInfo(closeChunk=True)


def get_skinCluster(inputObj):
    """

    Args:
        inputObj(str): find skin cluster and return skin cluster's name

    Returns:

    """
    try:
        skinCls = mel.eval("findRelatedSkinCluster(\"{}\")".format(inputObj))
    except:
        skinCls = None
    return skinCls

def undoSelectWrapper(func):
    @functools.wraps(func)
    def wrapFunc(*args, **kwargs):
        sl = cmds.ls(sl=True, l=True)
        cmds.undoInfo(openChunk=True)
        try:
            re = func(*args, **kwargs)
            return re
        except Exception as e:
            print(e)
        finally:
            if sl:
                cmds.select(sl)
            cmds.undoInfo(closeChunk=True)
    return wrapFunc

def get_skin_joints(inputMesh):
    skin = get_skinCluster(inputMesh)
    jntS = None
    if skin:
        jntS = cmds.skinCluster(skin, query=True, influence=True)
    # if skin:
    #     jntS = cmds.listConnections(skin + ".matrix", s=1, d=0)
    return jntS

def listSet(listA, listB, op):
    """返回所要求的并集交集或者差集"""
    if not isinstance(listA, list):
        return 0
    if not isinstance(listB, list):
        return 0
    returnList = []
    # 交集 = intersection;
    # 并集 = union;

    if op == "intersection":
        returnList = list(set(listA) & set(listB))

    elif op == "union":
        returnList = list(set(listA) | set(listB))

    elif op == "DifferenceSetA-B":
        returnList = list(set(listA) - set(listB))  # 求差集（项在listA中，但不在listB中）

    elif op == "DifferenceSetB-A":
        returnList = list(set(listB) - set(listA))  # 求差集（项在listB中，但不在listA中）

    elif op == "SymDifferenceSet":  # 对称差集
        returnList = list(set(listA) ^ set(listB))  # 对称差集（项在listA或listB中，但不会同时出现在二者中）

    return returnList

def check_pieces_btn_2315():
    mesh_all = cmds.ls('')

def connect_max(port='127.0.0.1:7100'):
    import maya.cmds as cmds
    if cmds.commandPort(port, query=True):
        cmds.commandPort(name=port, close=True)

    cmds.commandPort(name=port, sourceType='python')

def get_filter_transform_objs(lis):
    obj_lis = []
    if isinstance(lis, (str, unicode)):
        obj_lis = [lis]
    elif isinstance(lis, (list, tuple)):
        obj_lis = list(lis)
    return_lis = []
    if obj_lis:
        for obj in obj_lis:
            if '.' in obj:
                return_lis.append(obj.rpartition('.')[0])
            else:
                return_lis.append(obj)
    return list(set(return_lis))


def timeElapsedWithParameter(parameter):

    def wrapFunc(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            start = time.time()
            re = func(*args, **kwargs)
            end = time.time()
            print('{} Elapsed time: {}'.format(parameter, end-start))
            return re
        return inner

    return wrapFunc



