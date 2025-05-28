#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.api.OpenMaya as OpenMayaAPI
import maya.api.OpenMayaAnim as OpenMayaAnimAPI
import os
import pymel.core as pm
import arcUtils
import csv
import os,sys,time
reload(arcUtils)


def get_skin_influence(mesh=None, vtx_array=None):
    """
    Warnings: vtx_array 必须为数字列表
    Args:
        mesh:
        vtx_array:

    Returns:

    """
    if mesh is None and vtx_array is None:
        return cmds.warning('get what?')
    elif mesh is None and vtx_array is not None:
        vtx_array = arcUtils.return_list(vtx_array)
        mesh = vtx_array[0].split('.')[0]

    # ...get vtxID_Array
    shape = arcUtils.get_shape(mesh)
    if not shape:
        return cmds.warning('{} must be a mesh'.format(mesh))
    if cmds.objectType(shape) != 'mesh':
        return cmds.warning('{} must be a mesh, current is {}'.format(mesh, cmds.objectType(shape)))
    if vtx_array is None:
        vtx_array = list(range(0, len(cmds.ls('%s.vtx[*]' % mesh, fl=1))))
    else:
        vtx_array = [int(x.split('.')[-1].split('[')[-1].split(']')[0]) for x in vtx_array]

    # ...get skin
    selList = OpenMayaAPI.MSelectionList()
    selList.add(mel.eval('findRelatedSkinCluster %s' % mesh))
    skinPath = selList.getDependNode(0)

    # ...get mesh
    selList = OpenMayaAPI.MSelectionList()
    selList.add(mesh)
    meshPath = selList.getDagPath(0)

    # ...get vtxs
    fnSkinCluster = OpenMayaAnimAPI.MFnSkinCluster(skinPath)
    fnVtxComp = OpenMayaAPI.MFnSingleIndexedComponent()
    vtxComponents = fnVtxComp.create(OpenMayaAPI.MFn.kMeshVertComponent)
    fnVtxComp.addElements(vtx_array)

    # ...get weights/infs
    dWeights, infCount = fnSkinCluster.getWeights(meshPath, vtxComponents)
    # weights_Array = np.array(list(dWeights), dtype='float64')
    inf_Array = [dp.partialPathName() for dp in fnSkinCluster.influenceObjects()]
    return inf_Array, dWeights, infCount


def flatten(lst):
    return [item for sublist in lst for item in sublist]


def compose_3_element_to_str(lis, step=3):
    new_lis = [lis[i:i + step] for i in range(0, len(lis), step)]

    up_lis = []

    for la in new_lis:
        str_la = ','.join([str(x) for x in la])
        up_lis.append(str_la)

    return up_lis


def flatten_twoDimensional_array(array):
    """

    Args:
        array: [[1, 2, 3], [2, 3, 4]]

    Returns: 展平成[1, 2, 3, 2, 3, 4]输出

    """
    return [item for sub in array for item in sub]


def compose_weights_data(mesh, data_path='D:/work/data/weights/'):
    inf_array, weights, inf_count = get_skin_influence(mesh)
    parent_array = arcUtils.get_parent_array(inf_array)
    pos_array = []
    # for x in inf_array:
    #     pos = cmds.xform(x, q=1, ws=1, t=1)
    #     pos_array.append(pos[0])
    #     pos_array.append(pos[1])
    #     pos_array.append(pos[2])

    pos_array = compose_3_element_to_str(
        flatten_twoDimensional_array([cmds.xform(x, q=1, ws=1, t=1) for x in inf_array]))

    rot_array = compose_3_element_to_str(
        flatten_twoDimensional_array([cmds.xform(x, q=1, ws=1, ro=1) for x in inf_array]))

    weights_data_1 = [weights[i:i + inf_count] for i in range(0, len(weights), inf_count)]

    with open('{}{}.csw'.format(data_path, mesh), 'wb') as f:
        w = csv.writer(f, delimiter=' ', quoting=csv.QUOTE_NONE, escapechar=' ')
        w.writerow(['influence', ','.join(inf_array).replace('FBXASC032', ' ')])
        w.writerow(['influParent', ','.join(parent_array).replace('FBXASC032', ' ')])
        w.writerow(['influPos', ' '.join(pos_array)])
        # print(pos_array)
        w.writerow(['influRot', ' '.join(rot_array)])
        for i, data in enumerate(weights_data_1):
            weight_clear = ['{} {}'.format(t, cl) for t, cl in enumerate(data) if cl != 0]
            cur_data = '{index} {weight_clear}'.format(index=i, weight_clear=' '.join(weight_clear))

            w.writerow([cur_data])
    # 替换文件中所有的双空格为单空格
    with open('{}{}.csw'.format(data_path, mesh), 'r') as ff:
        content = ff.read()

    # print(content)

    updated_content = content.replace('  ', ' ')

    with open('{}{}.csw'.format(data_path, mesh), 'w') as ff:
        ff.write(updated_content)


def decompose_weights_data(mesh, data_path='D:/work/data/weights/'):
    # weights_data = []
    if not os.path.exists(data_path + mesh + '.csw'):
        return

    with open('{}{}.csw'.format(data_path, mesh), 'r') as f:
        mesh_data = f.readlines()
        if not mesh_data:
            return cmds.warning('{} has no skin data'.format(mesh))
        # print(mesh_data)
        weights_data = mesh_data[4:]

        jnts_data = mesh_data[0].rstrip().partition('influence ')[-1].replace('\n', '').split(',')

        # final joints in maya skinWeights
        jnts_recompose = [x.replace(' ', 'FBXASC032') for x in jnts_data]

        weights_full = []
        # 处理是否已有权重

        check_and_weights(mesh, jnts_recompose)

        jnts_skin = arcUtils.get_skin_joints(mesh)

        for t, weights_str in enumerate(weights_data):
            ssd = weights_str.replace('\n', '').split(' ')[1:]
            indices = [int(x) for x in ssd[0::2]]
            weights_c = [float(x) for x in ssd[1::2]]
            jnts_c = [jnts_recompose[x] for x in indices]

            weights_compose = [0] * len(jnts_skin)

            for i, jnt in enumerate(jnts_c):
                weights_compose[jnts_skin.index(jnt)] = weights_c[i]

            weights_full += weights_compose

        setWeights_api(mesh, weights_full)


def setWeights_api(mesh, weights):
    skinCluster = arcUtils.get_skinCluster(mesh)

    # get the MFnSkinCluster for skinCluster
    selList = OpenMaya.MSelectionList()
    selList.add(skinCluster)
    skinClusterMObject = OpenMaya.MObject()
    selList.getDependNode(0, skinClusterMObject)
    skinFn = OpenMayaAnim.MFnSkinCluster(skinClusterMObject)

    # Get dagPath and member components of skinned shape
    fnSet = OpenMaya.MFnSet(skinFn.deformerSet())
    members = OpenMaya.MSelectionList()
    fnSet.getMembers(members, False)
    dagPath = OpenMaya.MDagPath()
    components = OpenMaya.MObject()
    members.getDagPath(0, dagPath, components)

    ###################################################

    # ...set infs
    influencePaths = OpenMaya.MDagPathArray()
    infCount = skinFn.influenceObjects(influencePaths)
    influences_Array = [influencePaths[i].partialPathName() for i in range(influencePaths.length())]

    # ...change the order in set(i,i)
    influenceIndices = OpenMaya.MIntArray(infCount)
    [influenceIndices.set(i, i) for i in range(infCount)]

    ###################################################
    # ...set data
    weights_mArray = OpenMaya.MDoubleArray()
    for i, x in enumerate(weights):
        if x < 0.00000001:
            x = 0
        elif x > 0.9999999:
            x = 1
        weights_mArray.append(x)
    skinFn.setWeights(dagPath, components, influenceIndices, weights_mArray, False)
    # 规范化权重
    inf_jnts = arcUtils.get_skin_joints(mesh)
    for jnt in inf_jnts:
        cmds.setAttr(jnt + '.lockInfluenceWeights', 0)

    cmds.select(mesh, r=True)
    cmds.skinPercent(skinCluster, normalize=True)


def addInfluencesJnt(mesh, jntList):
    jnt_list = arcUtils.return_list(jntList)
    skinJnt = arcUtils.get_skin_joints(mesh)
    skinClusterName = arcUtils.get_skinCluster(mesh)
    add_jnts = [x for x in jnt_list if x not in skinJnt]

    cmds.skinCluster(skinClusterName, e=True, ai=add_jnts, lw=True, wt=0)
    [cmds.setAttr(x + '.liw', 0) for x in add_jnts]

    arcUtils.return_result('add influence:  {} to {}'.format(str(jntList), skinClusterName))


def move_skinWeights_jntToJnt(jnt_from, jnt_to, mesh):
    inf_array, weights, inf_count = get_skin_influence(mesh)

    if not inf_array:
        return cmds.warning('{} has no skin'.format(mesh))

    jnt_from_lis = arcUtils.return_list(jnt_from)
    jnt_to_lis = arcUtils.return_list(jnt_to)

    for i, (ff, tt) in enumerate(zip(jnt_from_lis, jnt_to_lis)):

        if ff not in inf_array:
            addInfluencesJnt(mesh, ff)
            # return cmds.warning('cannot pass weights from a joint not influence the mesh:{}'.format(mesh))

        if tt not in inf_array:
            # 添加不存在的蒙皮关节到skin节点
            addInfluencesJnt(mesh, tt)

    # 刷新当前蒙皮信息
    inf_array, weights, inf_count = get_skin_influence(mesh)
    # 赋予新的权重信息
    # index_to = inf_array.index(tt)
    # index_from = inf_array.index(ff)
    weights_new = []
    for i in range(0, len(weights), int(inf_count)):
        # 对应当前每一个点的影响权重关节列表

        cur_vtx_weights = weights[i: i + inf_count]
        for ff_jnt, tt_jnt in zip(jnt_from_lis, jnt_to_lis):
            index_from = inf_array.index(ff_jnt)
            index_to = inf_array.index(tt_jnt)
            cur_vtx_weights[index_to] = cur_vtx_weights[index_from] + cur_vtx_weights[index_to]
            cur_vtx_weights[index_from] = 0.0
        weights_new += cur_vtx_weights

    setWeights_api(mesh, weights=weights_new)

    arcUtils.return_result('moved weights from {} to {}'.format(jnt_from_lis, jnt_to_lis))


def check_and_addInfJnts(mesh, inf_jnts):
    skin_name = arcUtils.get_skinCluster(mesh)

    if skin_name:
        skin_jnts = arcUtils.get_skin_joints(mesh)
        non_deform_jnts = [x for x in inf_jnts if x not in skin_jnts]

        if non_deform_jnts:
            addInfluencesJnt(mesh, non_deform_jnts)


def check_and_weights(mesh, inf_jnts):
    skin_name = arcUtils.get_skinCluster(mesh)

    if skin_name:
        check_and_addInfJnts(mesh, inf_jnts)
    else:
        cmds.skinCluster(mesh, inf_jnts, tsb=1, mi=3,
                         bindMethod=0, skinMethod=0, lockWeights=False)


def transfer_skin_jntToJnt(fromJntList, toJntList, meshName=None):
    """
    transfer jnt skin weights to new jnt skin weights, and delete old jnt weights
    Args:
        meshName:
        fromJntList:
        toJntList:

    Returns:

    """
    with arcUtils.UndoFunc():

        with arcUtils.GetFilter('mesh') as Get:
            mesh = Get.filterObjs

        if mesh:
            mesh_sl = mesh[0]
        else:
            mesh_sl = None

        if not meshName:
            meshName = mesh_sl

        if not meshName:
            return cmds.warning('please select a mesh only')

        if not isinstance(meshName, (str, unicode)):
            return cmds.error(u"%s must a string" % meshName)

        fromJntL = []
        ToJntL = []
        if isinstance(fromJntList, (str, unicode)):
            fromJntL += [fromJntList]
        elif isinstance(fromJntList, list):
            fromJntL = fromJntList
        if isinstance(toJntList, (str, unicode)):
            ToJntL += [toJntList]
        elif isinstance(toJntList, list):
            ToJntL = toJntList
        if len(fromJntL) != len(ToJntL):
            return cmds.error(u"joint not compatible check out")
        meshShp = cmds.listRelatives(meshName, s=True)

        skinClusterName = arcUtils.get_skinCluster(meshName)
        # for i in range(len(skinC)):
        #     if cmds.objectType(skinC[i]) == "skinCluster":
        #         skinClusterName = skinC[i]
        if not skinClusterName:
            return cmds.error(u"no skinCluster")

        skinPrimeJntList = []  #
        inputList = cmds.listConnections(skinClusterName + ".matrix", s=1, d=0)
        if inputList:
            skinPrimeJntList += inputList

        with arcUtils.ProgressWin(len(fromJntL), 'transfer weights: ') as pr:
            for i, m in enumerate(fromJntL):
                pr.edit_window(i, "转移权重 %s --> %s" % (fromJntL[i], ToJntL[i]))
                if fromJntL[i] == ToJntL[i]:
                    continue
                else:
                    if ToJntL[i] not in skinPrimeJntList:
                        cmds.skinCluster(skinClusterName, e=True, ai=ToJntL[i], lw=True, ug=True, dr=4, ps=0, ns=10,
                                         wt=0)
                    cmds.setAttr(fromJntL[i] + ".liw", 0)
                    cmds.setAttr(ToJntL[i] + ".liw", 0)
                    cmds.select(clear=True)
                    cmds.skinCluster(skinClusterName, selectInfluenceVerts=fromJntL[i], e=True)
                    # 判断是否存在影响顶点，如果存在就转移，如果不存在就返回
                    allSelect = cmds.ls(sl=True, fl=True)
                    selectInfluenceVertex = [x for x in allSelect if x not in meshShp and x != skinClusterName]

                    if selectInfluenceVertex:  # 如果没有影响顶点 骨骼权重传递不了
                        cmds.skinPercent(skinClusterName, tmw=[fromJntL[i], ToJntL[i]])
                    cmds.skinCluster(skinClusterName, e=True, ri=fromJntL[i])


def normalize_and_clean_weights(mesh, threshold=0.0001):
    # 获取skinCluster
    mesh_skin_cluster = arcUtils.get_skinCluster(mesh)

    if not mesh_skin_cluster:
        print("No skin cluster found on mesh")
        return
    remove_unused_influences(mesh)
    cmds.select(mesh, r=True)

    mel.eval("doPruneSkinClusterWeightsArgList 1 w" + "{" + '\"{0}\" '.format(threshold) + "};")

    cmds.skinPercent(mesh_skin_cluster, normalize=True)


def get_splitFourWeights(weight_array, jnt_array):
    """
    返回矫正后的权重值和关节列表，以方便api设置权重
    Args:
        weight_array:
        jnt_array:

    Returns:

    """
    if len(weight_array) != len(jnt_array):
        cmds.warning('weight array not compatible with jnt array')
        return None

    dic = OrderedDict()
    zero_num = len([x for x in weight_array if x == 0.0])

    for weight, jnt in zip(weight_array, jnt_array):
        dic.update({jnt: weight})

    sort_dic = sorted(dic.items(), key=lambda t: t[1])
    # print(sort_dic)
    inf_sort = [dic.get(x[0]) for x in sort_dic[zero_num:]]
    jnt_sort = [x[0] for x in sort_dic[zero_num:]]

    while len(jnt_sort) > 4:
        cur_jnt = jnt_sort.pop(0)
        cur_weight = inf_sort.pop(0)
        dic[cur_jnt] = 0.0
        all_value = sum(inf_sort)
        inf_sort = [(float(x) * cur_weight / float(all_value) + x) for x in inf_sort]


    return dic.keys(), dic.values()


def get_noneFourInf_weightArray(weight_array, inf_array, id_array=None):
    """
    根据weight_array的数据，将所有关节的权重转换为4关节权重并返回新的weight_array

    Args:
        weight_array: one row weight array
        inf_array: the influence joint array

    Returns:

    """

    if not len(weight_array) or not len(inf_array):
        cmds.warning('weight array or influence array is empty.')
        return None
    vtx_check = len(weight_array) % len(inf_array)
    if vtx_check != 0:
        cmds.warning('the weight array not compatible wight the jnt array')
        return None
    vtx_num = len(weight_array) / len(inf_array)
    if vtx_num < 1:
        cmds.warning('the weight array can not be less than joint array')
        return None

    # vtx_array = []

    new_weight_array = []

    if id_array:
        ids = id_array
    else:
        ids = [x for x in range(0, vtx_num)]
    id_weight_array = []
    with arcUtils.ProgressWin(num=len(ids), label='calculating four weights:', return_result=False) as pr:

        for dex, i in enumerate(ids):
            # i = 6769
            # pr.edit_window(value=0, text='calculating vtx id: {}'.format(i))
            cur_weight_array = weight_array[int(i) * len(inf_array): (int(i) + 1) * len(inf_array)]

            #
            new_jnt, new_weight = get_splitFourWeights(cur_weight_array, inf_array)
            id_weight_array += new_weight
            # new_weight_array += new_weight
            pr.edit_window(value=dex)
    # break
    return id_weight_array


def set_noneFourWeight(vtx_array, weights_array):
    """将传入的点设置为4点权重"""
    mesh_lis = list(set([x.split('.')[0] for x in vtx_array]))
    if len(mesh_lis) != 1:
        return cmds.warning('can only operate one mesh parallel')
    # 将vtx_array转为id列表
    vtx_id_array = [int(x.split('.')[-1].split('[')[-1].split(']')[0]) for x in vtx_array]

    mesh = vtx_array[0].split('.')[0]

    skinCluster = arcUtils.get_skinCluster(mesh)
    old_jnt_array, old_weights_array, old_count = get_skin_influence(mesh)
    # get the MFnSkinCluster for skinCluster
    selList = OpenMaya.MSelectionList()
    selList.add(skinCluster)
    skinClusterMObject = OpenMaya.MObject()
    selList.getDependNode(0, skinClusterMObject)
    skinFn = OpenMayaAnim.MFnSkinCluster(skinClusterMObject)

    # Get dagPath and member components of skinned shape
    fnSet = OpenMaya.MFnSet(skinFn.deformerSet())
    members = OpenMaya.MSelectionList()
    fnSet.getMembers(members, False)
    dagPath = OpenMaya.MDagPath()
    components = OpenMaya.MObject()
    members.getDagPath(0, dagPath, components)

    ###################################################

    # ...set infs
    influencePaths = OpenMaya.MDagPathArray()
    infCount = skinFn.influenceObjects(influencePaths)
    influences_Array = [influencePaths[i].partialPathName() for i in range(influencePaths.length())]

    # ...change the order in set(i,i)
    influenceIndices = OpenMaya.MIntArray(infCount)
    [influenceIndices.set(i, i) for i in range(infCount)]

    ###################################################

    # reconstruct new weights 重新组织权重值
    for i, id_num in enumerate(vtx_id_array):
        old_weights_array[id_num * infCount: (id_num + 1) * infCount] = weights_array[i * infCount: (i + 1) * infCount]
    weights_mArray = OpenMaya.MDoubleArray()
    for i, x in enumerate(old_weights_array):
        if x < 0.00000001:
            x = 0
        elif x > 0.9999999:
            x = 1
        weights_mArray.append(x)
    skinFn.setWeights(dagPath, components, influenceIndices, weights_mArray, False)
    # 规范化权重
    inf_jnts = arcUtils.get_skin_joints(mesh)
    for jnt in inf_jnts:
        cmds.setAttr(jnt + '.lockInfluenceWeights', 0)
    cmds.select(vtx_array)
    cmds.skinPercent(skinCluster, normalize=True)


# 删除没有权重的骨骼
def remove_unused_influences(mesh):
    influence_joints = arcUtils.get_skin_joints(mesh)
    skinCluster = arcUtils.get_skinCluster(mesh)
    if not skinCluster:
        return
    for joint in influence_joints:
        # 获取该骨骼对所有顶点的权重
        weights = cmds.skinPercent(skinCluster, joint, query=True, value=True)

        # 检查是否所有的权重都为0
        if all(weight == 0 for weight in weights):
            # 移除骨骼的影响
            cmds.skinCluster(skinCluster, edit=True, removeInfluence=joint)
    print('移除骨骼成功！')

def set_allInf_to_four(meshes=None, sl_vtx=None):
    # 先将所有的mesh和sl_vtx归类成每个模型和每个每个模型上的点，方便操作
    # 比如，如果meshes里有模型A,sl_vtx也有模型A的点，那么就屏蔽模型A,只去计算点
    # ################################
    # 如果meshes和sl_vtx都为空，报错返回，不操作
    # 如果meshes为空，sl_vtx不为空，则对应操作相应的点即可
    # 反之，meshes不为空，sl_vtx为空，则去计算所有meshes里的所有模型的所有点
    vtx_dic = {}
    # 需要只传给最终权重（只有超过4点影响的点）
    # 1. 将选择的点分类，按照mesh:id的键值进行字典组建(注意，程序设置sl_vtx 和meshes如果有相同模型，会自动屏蔽其一）
    if sl_vtx:
        lis = arcUtils.return_list(sl_vtx)
        meshs = list(set([x.split('.')[0] for x in lis]))
        for m in meshs:
            m_id = [vv.split('.')[-1].split(']')[0].split('[')[-1] for vv in lis if vv.startswith(m)]
            vtx_dic.update({m: m_id})

    if meshes:
        none_four_vtx, dic = get_jntWeightFourMore_Vtx(meshes)

        if none_four_vtx:
            vtx_dic.update(dic)

    if not vtx_dic:
        return cmds.warning('no vtx array\'s can operate')

    with arcUtils.ProgressWin(num=len(vtx_dic.keys()), label='clear ') as pr:
        for i, key in enumerate(vtx_dic.keys()):

            pr.edit_window(i, key)
            # remove unused skin joints
            # remove_unused_influences(key)
            jnt_array, weights_array, count = get_skin_influence(key)
            ids = vtx_dic[key]
            new_weights = get_noneFourInf_weightArray(weights_array, jnt_array, id_array=vtx_dic[key])

            full_id_array = [range(int(id)*len(jnt_array), (int(id)+1)*len(jnt_array), 1) for id in ids]
            # print(len(weights_array)*len)
            full_id_array = flatten(full_id_array)

            for id, weight in zip(full_id_array, new_weights):

                weights_array[id] = weight

            setWeights_api(mesh=key, weights=weights_array)
            # set_noneFourWeight(vtx_array, new_weights_array)
            # pr.edit_window(100, vtx_array[0].split('.')[0])


def set_vertex_weight_api(vtx_id, mesh, weights):

    # 获取当前选择的物体
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection)
    dagPath = OpenMaya.MDagPath()
    selection.getDagPath(0, dagPath)

    # 以读取和修改的方式打开当前选择的物体
    meshFn = OpenMaya.MFnMesh(dagPath)

    # 获取顶点权重
    weights = OpenMaya.MDoubleArray()
    vertexIndex = 0  # 这里假设您要操作的顶点的索引是0
    meshFn.getVertexWeights(dagPath.instanceNumber(), vertexIndex, weights)

    # 设置新的权重
    newWeight = 0.5
    weights.set(newWeight, vertexIndex)
    meshFn.setVertexWeights(dagPath.instanceNumber(), vertexIndex, weights, False)


def get_jntWeightFourMore_Vtx(meshes):
    """
    获取点权重影响骨骼大于4的点
    Args:
        meshes:

    Returns:

    """
    mesh_lis = arcUtils.return_list(meshes)

    # 获取形节点，将所有模型加入列表并剔除非模型物体
    real_meshes = []
    if mesh_lis:
        # convert all objs to transform nodes
        mesh_lis = arcUtils.get_filter_transform_objs(mesh_lis)
        for obj in mesh_lis:
            shape = arcUtils.get_shape(obj)
            if cmds.objectType(shape) == 'mesh':
                real_meshes.append(obj)

    if not real_meshes:
        return cmds.warning('no mesh selected.')

    none_zero_dic = {}

    for mesh in real_meshes:
        vtx_array = cmds.ls(mesh + '.vtx[:]', fl=True)
        # get skin influences
        inf_array, weights_array, count = get_skin_influence(mesh)
        none_zero_vtx = []
        with arcUtils.ProgressWin(num=len(vtx_array), label='{} calculating'.format(mesh)) as pr:

            for i in range(0, len(vtx_array)):
                pr.edit_window(value=i)
                cur_weights = weights_array[i * len(inf_array):len(inf_array) * (i + 1)]

                non_zero = [x for x in cur_weights if x != 0.0]

                if len(non_zero) > 4:
                    none_zero_vtx.append(i)

        none_zero_dic.update({mesh: none_zero_vtx})

    vtx_all = []
    vtx_series = []
    vtx_ser_dic = {}
    for mesh, mesh_vtx_lis in none_zero_dic.iteritems():
        if mesh_vtx_lis:
            cur_vtx = ['{}.vtx[{}]'.format(mesh, i) for i in mesh_vtx_lis]

            vtx_all += cur_vtx
            vtx_series.append(cur_vtx)
            vtx_ser_dic.update({mesh: mesh_vtx_lis})
            # print('\n')
            cmds.warning('{} has -{}- vertex\'s influence more than four'.format(mesh, len(mesh_vtx_lis)))

        else:
            arcUtils.return_result('Congratulations! -{}- all in set!'.format(mesh))

    return vtx_all, vtx_ser_dic





def copySkinWeight_commonTools():
    """
    拷贝权重，先选择权重好的物体，在选择需要拷贝的物体
    最大影响无限制
    """
    sel = pm.selected()
    jnt = pm.skinCluster(sel[0], q=True, inf=True)
    for i in sel[1:]:
        newSkin = pm.mel.findRelatedSkinCluster(i)
        if newSkin != "":
            pm.delete(newSkin)
        pm.skinCluster(i, jnt, tsb=True)
        pm.copySkinWeights(sel[0], i, noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="oneToOne")


def querySelecteModelSkinJnt():
    """
    查询所选物体的蒙皮骨骼
    """
    sel = pm.selected()
    selectSkinList = []
    for i in sel:
        # skinClusterName = pm.mel.findRelatedSkinCluster(i)
        # allSkin = pm.skinCluster(skinClusterName, q = True, inf = True)
        allSkin = pm.skinCluster(i, q=True, inf=True)
        for skin in allSkin:
            if skin not in selectSkinList:
                selectSkinList.append(skin)
    pm.select(selectSkinList)
    return selectSkinList


def getJointAllChildren(inputJnt, outputJnt):
    """
    返回选择物体以及下面所有层级的物体
    inputJnt :选择的骨骼
    outputJnt : []
    """
    for ii in inputJnt:
        outputJnt.append(ii)

        getchilds = ii.getChildren(type="joint")

        if (getchilds) != None:
            getJointAllChildren(getchilds, outputJnt)
    return outputJnt


def importTempFbxToMaya():
    tempPath = os.getenv('TEMP')
    cmds.file(tempPath + "\zzz.FBX", pr=1, ignoreVersion=1, i=1, type="FBX", importFrameRate=True, namespace=":",
              importTimeRange="override", ra=True, mergeNamespacesOnClash=True, options="v=0;")


def addInfJoints():
    """
       添加权重影响
    """
    objList = cmds.ls(sl=1)
    mesh = []
    joint = []

    # 筛选选择的骨骼与模型
    for obj in objList:
        if cmds.objectType(obj) == 'joint':
            joint.append(obj)
        else:
            objShape = cmds.listRelatives(obj, shapes=True)[0]
            if cmds.objectType(objShape) == 'mesh':
                mesh.append(obj)

    # 将所有的骨骼模型添加影响
    for obj in mesh:
        skinClusterName = pm.mel.findRelatedSkinCluster(obj)
        cmds.skinCluster(skinClusterName, edit=True, ai=joint, lw=1, wt=0)


def weightClear(skinName='skinCluster', geoName='geo', clearMinWeight=0.0001):
    ''' weightClear'''
    # unlock all joint
    jointList = [jE for jE in cmds.ls(type='joint') if cmds.objExists('%s.liw' % jE)]
    for jE in jointList:
        cmds.setAttr('%s.liw' % jE, False)
    # getWeight and clear
    allWeightList = cmds.getAttr('%s.wl[*].w' % skinName)
    # default

    cmds.skinPercent(skinName, geoName, prw=clearMinWeight)
    # setWeight

    wlAttrList = cmds.ls('%s.wl[*]' % skinName)
    for i in range(len(wlAttrList)):
        cmds.setAttr('%s.w[*]' % (wlAttrList[i]), *allWeightList[i])
    # normalize
    cmds.skinPercent(skinName, geoName, normalize=True)


def buttonCommand_weightClear(minWeight):
    '''
    清理并规格化小权重
    '''
    # weight
    # apply
    sel = cmds.ls(sl=True)
    for sl in sel:
        skinList = pm.listHistory(sl, pdo=1, type='skinCluster')
        if not skinList:
            continue
        weightClear(skinName=skinList[0].name(), geoName=sl, clearMinWeight=minWeight)


def buttonCommand_checkInflunce(num = 4):
    ''' buttonCommand_checkInflunce'''

    def check_LimitSize(geoGrpName='geo', limitSize=4):
        ''' check_LimitSize'''
        exLimitList = []
        geometryList = set([mE.getParent() for mE in pm.listRelatives(geoGrpName, ad=True, type='mesh')])
        for geoE in geometryList:
            skinList = geoE.listHistory(pdo=True, type='skinCluster')
            if skinList:
                vtxSize = pm.polyEvaluate(geoE, v=True)
                for i in range(vtxSize):
                    weightList = skinList[0].wl[i].w.get()
                    if len(weightList) > limitSize:
                        exLimitList.append(geoE.vtx[i].name())
        return exLimitList

    tempList = []
    for sl in cmds.ls(sl=True):
        tempList += check_LimitSize(sl, int(num))

    cmds.select(tempList)


def buttonCommand_forceClear(num = 4):
    ''' '''
    # time count
    saveTime = time.time()

    clearSize = int(num)

    def forceClearList(refTuple=[]):
        ''' '''
        # check too short
        if len(refTuple) <= clearSize:
            pass
            #return outList
        # normalize list
        refList = list(refTuple)
        sortList = sorted(refList, reverse=True)
        for i, rE in enumerate(refList):
            if rE in sortList[clearSize:]:
                refList[i] = 0.0
        mutValue = 1 / sum(refList)
        outList = [rE * mutValue for rE in refList]
        return outList

    def forceClear(geoGrpName='geo', limitSize=4):
        ''' forceClear'''
        geometryList = set([mE.getParent() for mE in pm.listRelatives(geoGrpName, ad=True, type='mesh')])
        for geoE in geometryList:
            skinList = geoE.listHistory(pdo=True, type='skinCluster')
            if not skinList:
                continue
            vtxSize = pm.polyEvaluate(geoE, v=True)
            for i in range(vtxSize):
                weightList = skinList[0].wl[i].w.get()
                if len(weightList) > limitSize:
                    for wE, wVE in zip(cmds.ls(skinList[0].wl[i].w.name() + '[*]'), forceClearList(weightList)):
                        cmds.setAttr(wE, wVE)
            # normalize
            pm.skinPercent(skinList[0].name(), geoE, normalize=True)

    for sl in cmds.ls(sl=True):
        forceClear(sl, clearSize)

    # time count
    print('%s    use    %s    sec' % (sys._getframe().f_code.co_name, time.time() - saveTime))

# objA是字符串类型，objB是点的列表
def CopySkin_OneToOne(objA, objB):

    #查看objA有没有蒙皮节点
    ObjASkinName = pm.mel.findRelatedSkinCluster(objA)


    if ObjASkinName == "":
        print(objA + "no have skinNode")
        return None
    # 获取A的骨骼影响数
    else:
        ObjAInfJoint = pm.skinCluster(objA, q=True, inf=True)


    # 判断objB属于模型的点列表
    if ".vtx" in objB[0]:


        objBName = objB[0].split(".")[0]
        ObjBSkinName = pm.mel.findRelatedSkinCluster(objBName)
        #判断objB是否存在蒙皮节点，若不存在直接复制权重即可
        if ObjBSkinName == "":
            pm.skinCluster(objBName, ObjAInfJoint, tsb=True)
            pm.copySkinWeights(objA, objBName, noMirror=True, surfaceAssociation="closestPoint",
                               influenceAssociation="oneToOne")
            return True
        # 该列表的模型
        if ObjBSkinName != "":
            ObjBInfJoint = pm.skinCluster(objBName, q=True, inf=True)

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

            pm.skinCluster(objBName, ObjAInfJoint, tsb=True)
            pm.copySkinWeights(objA, objBName, noMirror=True, surfaceAssociation="closestPoint",
                               influenceAssociation="oneToOne")

    # 判断objB属于模型
    else:
        newSkin = pm.mel.findRelatedSkinCluster(objB[0])
        if newSkin != "":
            pm.delete(newSkin)
        else :
            pm.skinCluster(objB[0], ObjAInfJoint, tsb=True)
            pm.copySkinWeights(objA, objB[0], noMirror=True, surfaceAssociation="closestPoint",
                           influenceAssociation="oneToOne")
    return True


def relax_pointWeight(objects ,stepsNum ,stepsSize ):
    args = {}
    args['numSteps'] = stepsNum
    args['stepSize'] = stepsSize

    cmds.ngSkinRelax(objects, **args)

