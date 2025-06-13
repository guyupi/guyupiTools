# /usr/bin/env python
# -*- coding: UTF-8 -*-
import maya.cmds as cmds
import maya.OpenMaya as om
from collections import Counter
from ...UI.uiClass.mayaPrint import printTool
import re

class ReName():

    def __init__(self):
        pass

    def get_LongNameByUuid(self, uuid):
        # 获取长名称
        obj_loneName = cmds.ls(uuid, uuid=True,long = True)

        if len(obj_loneName) == 1:
            return obj_loneName[0]
        else:
            return None

    def get_uuidByLongName(self, longName):

        # 通过物体的名称，名称获取uuid
        uuid = cmds.ls(longName, uuid=1)[0]
        return uuid

    def get_longNameByName(self,name):
        longName = cmds.ls(name,long = True)[0]
        return longName


    def Rename(self, uuid, new_name):
        longName = self.get_LongNameByUuid(uuid)
        # result = cmds.ls(uuid=1 ,long = 1)

        self.maya_rename(longName ,new_name)

    def maya_rename(self , oldName ,new_name):

        try:
            cmds.rename(oldName, new_name)
        except:
            return


    def get_uuidList(self,*args):

        uuidList = []
        for obj in args:
            long_name = self.get_longNameByName(obj)
            uuidList.append(self.get_uuidByLongName(long_name))
        return uuidList


    def edit_prefix_suffix(self, objList, pre=None, suffix=None, edit_type=True):

        #获取uuid的列表
        uuidList = self.get_uuidList(*objList)

        for obj ,uuid in zip(objList,uuidList):

            obj_name = self.get_LongNameByUuid(uuid)

            sort_name = obj_name.split("|")[-1]

            new_name = sort_name
            # print new_name
            if edit_type:

                if pre:
                    new_name = pre + new_name

                if suffix:
                    new_name = new_name + suffix
            else:

                if pre:

                    if pre == new_name[0:len(pre)]:
                        new_name = new_name[len(pre):]

                if suffix:

                    if suffix == new_name[len(suffix) * -1:]:
                        new_name = new_name[:len(suffix) * -1]

            result = self.get_LongNameByUuid(uuid)
            self.maya_rename(result ,new_name)


    def Replace_name(self , objList, search  ,replace):
        uuidList = self.get_uuidList(*objList)

        for obj , uuid in zip(objList ,uuidList):

            obj_name = self.get_LongNameByUuid(uuid)

            sort_name = obj_name.split("|")[-1]

            new_name = sort_name

            if search in new_name:
                new_name = new_name.replace(search , replace)

            result = self.get_LongNameByUuid(uuid)

            self.maya_rename(result, new_name)



    def batch_Rename(self , objList , new_name = None):

        """
            使用re模块将字符串中的所有特殊字符替换为下划线
            """
        # 定义特殊字符的正则表达式模式，这里匹配非单词字符（字母、数字、下划线）和非空白字符
        if not new_name:
            return
        special_char_pattern = re.compile(r'[^\w]')

        # 使用sub函数进行替换，将匹配到的特殊字符替换为下划线
        mid_name = special_char_pattern.sub('_', new_name)

        uuidList = []
        for obj in objList:
            long_name = cmds.ls(obj ,long = 1)[0]
            uuid = cmds.ls(long_name,uuid = 1)[0]
            uuidList.append(uuid)

        for num ,uuid in enumerate(uuidList):

            new_name = mid_name + ("_{:02d}".format(num + 1))
            long_name = cmds.ls(uuid ,uuid = True ,long = True)

            self.maya_rename(long_name , new_name)


    def uuid_rename(self ,obj , new_name = None):
        uuidList = []
        long_name = cmds.ls(obj ,long = 1)[0]
        uuid = cmds.ls(long_name,uuid = 1)[0]

        self.Rename(uuid , new_name)

    def check_duplicate_names(self ):
        lst = cmds.ls(assemblies=True, dag=1, sn=1)
        # 使用 Counter 统计每个元素的出现次数
        count = Counter(lst)
        # 筛选出出现次数大于 1 的元素
        duplicates = [name for name in lst if "|" in name]

        if duplicates:
            cmds.select(duplicates)
            return duplicates
        else:
            print(u"Congratulations No duplicate names!!")


    def remove_nameSpace(self):
        # 清理命名空间
        ex_references = cmds.ls(type='reference')
        if ex_references:
            printTool.mayaError(u'场景中存在引用节点，无法删除名称空间')
            return
        namespaces = cmds.namespaceInfo(lon=True, recurse=True)

        if namespaces:
            # Exclude default namespaces
            default_namespaces = [':', 'UI', 'shared']
            namespaces = [ns for ns in namespaces if ns not in default_namespaces]
            # Sort namespaces by length in reverse order to delete child namespaces first
            namespaces.sort(key=lambda ns: len(ns), reverse=True)

            for ns in namespaces:
                cmds.namespace(moveNamespace=(ns, ':'), force=True)
                cmds.namespace(removeNamespace=ns)
            printTool.mayaPrint()

Name = ReName()



