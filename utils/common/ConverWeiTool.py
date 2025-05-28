#!/usr/bin/python
# -*- coding:utf-8 -*-
#weights.py
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.api.OpenMaya as OpenMayaAPI
import maya.api.OpenMayaAnim as OpenMayaAnimAPI
from ..rigging import skinWeightUtils
reload(skinWeightUtils)

class ConvertWeiTool(skinWeightUtils.SkinWeight):

    def __init__(self,mesh ,rootJoint ,sepJointList, headJointList = None,Type=1 , Degree=3  ,Percent = 80.0 ,openOrClose=1):
        self.mesh = mesh
        self.sepJointList = sepJointList
        self.rootJoint = rootJoint
        self.headJointList = headJointList
        self.Type = Type
        self.Degree = Degree
        self.Percent = Percent
        self.openOrClose = openOrClose


    def create_CvByJoint(self,jointList = None):

        if not jointList:
            jointList = [self.rootJoint] + self.sepJointList

        # Type 取值是 1 - 2 1为one to one   2为 ofset one

        curve = ""
        if self.Type == 1:
            # cvIdx 如果是one to one 子骨骼对应的cv点从1开始
            # cvIdx 如果是one to one 子骨骼对应的cv点从2开始
            cvIdx = 1
            # ofsWet 如果是one to one 并且百分比非100两个点上下偏移量一样
            # ofsWet 如果是ofset one 并且百分比非100 向上偏移的点力度为0.2
            ofsWet = 1
            # sepJots = self.sepJointList[:]#每一个骨骼都要分割权重
            points = [cmds.xform(j, q=True, ws=True, t=True) for j in jointList]
        # --Convert Type :Offset One
        elif self.Type == 2:
            cvIdx = 2
            ofsWet = 0.2
            points = [cmds.xform(j, q=True, ws=True, t=True) for j in jointList]
            # sepJots = self.sepJointList[:-1]#末端骨骼没有权重
        elif self.Type == 3:
            cvIdx = 2
            ofsWet = 0.2
            txVal = cmds.getAttr("%s.tx" % self.sepJointList[-1])
            # print "aaa",self.sepJointList[-1],txVal
            tempEndJot = cmds.createNode("joint", p=self.sepJointList[-1])
            cmds.setAttr(".tx", txVal)
            self.sepJointList.append(tempEndJot)
            points = [cmds.xform(j, q=True, ws=True, t=True) for j in ([self.rootJoint] + self.sepJointList)]
            sepJots = self.sepJointList[:-1]  # 末端骨骼没有权重
        if self.openOrClose == 1:  # Open
            if self.Percent == 100.0:
                # print  points, Degree
                curve = cmds.curve(p=points, d=self.Degree)
            else:
                points2 = []
                # evVec = []
                # 除了首尾每个位置两个点
                for idx, p in enumerate(points):
                    if idx == 0:
                        points2.append(p)
                    elif idx == len(points) - 1:
                        points2.append(p)
                    else:
                        # 滑动每个cv点
                        preMPt = om.MPoint(*points[idx - 1])
                        theMPt = om.MPoint(*p)
                        nexMPt = om.MPoint(*points[idx + 1])
                        prePoint = theMPt + (preMPt - theMPt) * (self.Percent * ofsWet / 100.0)
                        nexPoint = theMPt + (nexMPt - theMPt) * (self.Percent / 100.0)
                        points2.append([prePoint[0], prePoint[1], prePoint[2]])
                        # points2.append( p )
                        points2.append([nexPoint[0], nexPoint[1], nexPoint[2]])
                curve = cmds.curve(p=points2, d=self.Degree + 1)
        elif self.openOrClose == 2:  # Close
            spans = len(points)
            curve = cmds.circle(d=3, s=spans, ch=False)[0]
            for idx, p in enumerate(points):
                cmds.xform("%s.cv[%d]" % (curve, idx), ws=True, t=p)

        return curve

    def copy_mesh(self,mesh):
        wire_mesh = cmds.duplicate(self.mesh)[0]
        return  wire_mesh

    def build_wire(self,objList):
        if objList == "":
            objList = cmds.ls(sl=True)
        cvs = objList[0:-1]
        geo = objList[-1]
        wires = []
        for cv in cvs:
            newWire = cmds.deformer(geo, type="wire")[0]
            wire = cmds.rename(newWire, "wire_%s" % cv)
            wires.append(wire)
            cmds.setAttr("%s.rotation" % wire, 0)
            cmds.setAttr("%s.dropoffDistance[0]" % wire, 10000)
            base_cv = "%sBaseWire" % cv
            if not cmds.objExists(base_cv):
                new_cv = cmds.duplicate(cv)[0]
                base_cv = cmds.rename(new_cv, base_cv)
            cmds.hide(base_cv)
            cmds.connectAttr("%s.worldSpace[0]" % cv, "%s.deformedWire[0]" % wire)
            cmds.connectAttr("%s.worldSpace[0]" % base_cv, "%s.baseWire[0]" % wire)
        cmds.select(geo)
        return wires


    def build_cluster(self,curve):
        cvIdxStart = 0

        if self.Type == 1:
            cvIdx = 1
            jointList = self.sepJointList
        elif self.Type == 2:
            cvIdx = 2
            jointList = self.sepJointList[:-1]
        elif self.Type == 3:
            cvIdx = 2


        handl_list = []
        for idx in range(len(jointList)):
            if self.Percent == 100.0:
                # 一个骨骼一个cv点           one2one / offset One
                sInf = "%s.cv[%d]" % (curve, cvIdxStart + cvIdx)
                cvIdxStart += 1
            else:
                # 一个骨骼两个cv点           one2one / offset One
                sInf = ["%s.cv[%d]" % (curve, cvIdxStart + cvIdx),
                        "%s.cv[%d]" % (curve, cvIdxStart + cvIdx + 1)]
                cvIdxStart += 2
            cmds.select(sInf)
            clst, handl = cmds.cluster()

            handl_list.append(handl)
            dInf = self.sepJointList[idx]
        return handl_list

    def move_jointWeightsToDeform(self,deform, model, vertexs, weights):
        """
        deform :  变形器名称  允许cluster flexors, and user-defined deformers
        """
        defmObj = self.get_MDependNode(deform)
        modelPth, compsObj = self.get_vtxMobject(model, vertexs)

        print(defmObj)

        # Build weight float array
        wetsArray = om.MFloatArray()
        for v in weights:
            wetsArray.append(v)
        # Set weights once
        wetFilterFn = oma.MFnWeightGeometryFilter(defmObj)

        try:
            wetFilterFn.setWeight(modelPth, compsObj, wetsArray)
        except:
            raise Warning(deform, model, vertexs)
        return True


    def get_clusterWei(self , mesh ,deform):

        #移动后的模型点信息获取
        cmds.select(deform)
        cmds.move(0, 1, 0)
        mesh_dagPath = self.get_MPathByName(mesh)
        move_mesh_fn = om.MFnMesh(mesh_dagPath)
        weights = om.MDoubleArray()
        move_points = move_mesh_fn.numVertices()
        #移动前的点信息获取
        copy_mesh = self.copy_mesh(mesh)
        mesh_dagFath = self.get_MPathByName(copy_mesh)
        base_points = om.MPointArray()
        mesh_fn = om.MFnMesh(mesh_dagFath)
        mesh_fn.getPoints(base_points)

        # 创建顶点迭代器
        # move_points = om.MItMeshVertex(mesh_dagPath)
        for num in range(move_points):
            # 获取变形后的点位置
            point = om.MPoint()
            move_mesh_fn.getPoint(num, point, om.MSpace.kWorld)
            base_point = base_points[num].y
            # 移动到下一个顶点
            wei = point.y - base_point
            wei = round(wei , 5)
            weights.append( wei)

        cmds.select(deform)
        cmds.delete(copy_mesh)
        cmds.move(0, 0, 0)

        return weights

