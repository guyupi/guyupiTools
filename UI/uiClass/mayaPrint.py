#!/usr/bin/python
# -*- coding:utf-8 -*-
#scriptName publicClass.py
#
import maya.cmds as cmds

import maya.OpenMaya as om
import time
import sys
import re
import os
import maya.mel as mel

# class MayaPrint():
#     def __init__(self):
#         self.printerWinName = "self_printerWinName"
#         if mc.window(self.printerWinName,exists=1):
#             mc.deleteUI(self.printerWinName)
#
#     def mayaPrint(self,*arg,**args):#newWin=False,colour=[0,0.5,0],addResult=True,command="pass"):
#         """
#         """
#         argList = ["newWin","colour","addResult","command","autoShow","buttonType"]
#         for key in args:
#             if key not in argList:
#                 #raise "flagError","no flag %s"%key
#                 raise "TypeError"," Invalid flag: %s # "%( key )
#         #set flag default value
#         if argList[0] not in args:
#             args["newWin"]=False
#         if argList[1] not in args:
#             args["colour"]=[0,0.5,0]
#         if argList[2] not in args:
#             args["addResult"]=True
#         if argList[3] not in args:
#             args["command"]="pass"
#         if argList[4] not in args:
#             args["autoShow"]=True
#         if argList[5] not in args:
#             args["buttonType"]="iconTextButton"
#         #make old command can using
#         string = arg[0]
#         if len(arg)>1:
#             args["newWin"] = arg[1]
#         if len(arg)>2:
#             args["colour"] = arg[2]
#         if len(arg)>3:
#             args["addResult"] = arg[3]
#         if len(arg)>4:
#             args["command"] = arg[4]
#         if len(arg)>5:
#             args["autoShow"] = arg[5]
#         if len(arg)>6:
#             args["buttonType"] = arg[6]
#
#         if args["addResult"]:
#             result = 'Result:%s\n'%(string)
#             self.printerWin('Result:%s'%(string),args["newWin"],args["colour"],args["command"],args["autoShow"],args["buttonType"])
#         else:
#             result = '%s\n'%(string)
#             self.printerWin( string, args["newWin"], args["colour"], args["command"] ,args["autoShow"],args["buttonType"])
#         sys.stderr.write(result)
#
#     def mayaWarning(self,*arg,**args):#def mayaWarning(self,string,newWin=False,colour=[0.5,0,0.5],command="pass"):
#         """
#         """
#         argList = ["newWin","colour","command","autoShow"]
#         for key in args:
#             if key not in argList:
#                 #raise "flagError","no flag %s"%key
#                 raise "TypeError"," Invalid flag: %s # "%( key )
#         #set flag default value
#         if argList[0] not in args:
#             args["newWin"]=False
#         if argList[1] not in args:
#             args["colour"]=[0.5,0,0.5]
#         if argList[2] not in args:
#             args["command"]="pass"
#         if argList[3] not in args:
#             args["autoShow"]=True
#         #make old command can using
#         string = arg[0]
#         if len(arg)>1:
#             args["newWin"] = arg[1]
#         if len(arg)>2:
#             args["colour"] = arg[2]
#         if len(arg)>3:
#             args["command"] = arg[3]
#         if len(arg)>4:
#             args["autoShow"] = arg[4]
#         om.MGlobal.displayWarning("%s"%(string))
#         self.printerWin("#Warning:%s"%(string), args["newWin"], args["colour"], args["command"] ,args["autoShow"])
#
#     def mayaError(self,*arg,**args):#def mayaError(self,string,newWin=False,colour=[.5,0,0],command="pass"):
#         """
#         """
#         argList = ["newWin","colour","command","autoShow"]
#         for key in args:
#             if key not in argList:
#                 #raise "flagError","no flag %s"%key
#                 raise "TypeError"," Invalid flag: %s # "%( key )
#         #set flag default value
#         if argList[0] not in args:
#             args["newWin"]=False
#         if argList[1] not in args:
#             args["colour"]=[.5,0,0]
#         if argList[2] not in args:
#             args["command"]="pass"
#         if argList[3] not in args:
#             args["autoShow"]=True
#         #make old command can using
#         string = arg[0]
#         if len(arg)>1:
#             args["newWin"] = arg[1]
#         if len(arg)>2:
#             args["colour"] = arg[2]
#         if len(arg)>3:
#             args["command"] = arg[3]
#         if len(arg)>4:
#             args["autoShow"] = arg[4]
#         om.MGlobal.displayError("%s"%(string))
#         self.printerWin("# Error:%s"%(string), args["newWin"], args["colour"], args["command"] ,args["autoShow"])
#
#     def printerWin(self,string,onOff,colour,command,autoShow,buttonType="iconTextButton"):
#         if onOff:
#             winName = self.printerWinName
#             rootlayout = "digital_printerRootLayout_Win"
#             if not mc.window(winName,exists=True):
#                 win = mc.window(winName,title=" | Print Window ...")
#                 scroLayout = mc.scrollLayout( childResizable=True )
#                 mc.columnLayout( rootlayout ,adj=True)
#                 #mc.window(winName,e=True,w=1,h=1)
#                 #mc.window(winName,e=True,w=400,h=500)
#             if buttonType=="iconTextButton":
#                 mc.iconTextButton(label=string,c=command,bgc=colour,p=rootlayout,align="left",style="iconAndTextHorizontal",h=20,labelOffset=1,font="smallPlainLabelFont")
#             else:
#                 mc.text(label=string,align="left")
#             if autoShow==True:
#                 mc.showWindow(winName)
#
#     def funtionFlag(self,flagAndValue,**flags):
#         """funtionFlag:
#         check and set flag value;
#         return flagDirect;
#         flagAndValue like this: {"flagName":(value,type)}
#         **flags:read user input
#         like this:
#
#         defineFlags = {"m":(0,int),"wt":('',str,u'',unicode),"ft":('',str,u'',unicode)}
#         flagDirect = self.funtionFlag(defineFlags,**flags)
#         ##read from flagDirect
#         m = flagDirect["m"]
#         ft = flagDirect["ft"]
#
#         """
#         flagList = flagAndValue.keys()
#         defaultValueList = flagAndValue.values()
#
#         for flag in flags:
#             #check Invalid flag
#             if flag not in flagList:
#                 raise TypeError( " Invalid flag: %s # "%( flag ) )
#             #check value type
#             else:
#                 type_value = type( flags[ flag ] )
#                 raiseIt = True
#                 for i in range(1, len(flagAndValue[ flag ]) , 2):
#                     type_ = flagAndValue[ flag ][i]
#                     if type_value == type_:
#                         raiseIt = False
#                     elif flags[ flag ]==None and flags[ flag ] == flagAndValue[ flag ][i]:
#                         raiseIt = False
#                 if raiseIt == True:
#                     stype = [flagAndValue[ flag ][i] for i in range(1, len(flagAndValue[ flag ]) , 2)]
#                     raise TypeError( " Flag '%s' must be passed a %s argument # "%( flag, stype ) )
#         #set flag value
#         flagDirect = {}
#         for i in range( len(flagList) ):
#             flag = flagList[i]
#             if flag not in flags:
#                 #default value
#                 flagDirect[ flag ] = defaultValueList[i][0]
#             else:
#                 #user set value
#                 flagDirect[ flag ] = flags[flag]
#         return flagDirect
#
# printTool = MayaPrint()


class MayaPrint():

    #正常打印
    def mayaPrint(self ,printstr):
        # 在 Maya 脚本编辑器中显示信息
        om.MGlobal.displayInfo(printstr)
    #错误打印
    def mayaError(self ,warning_message):
        # 显示警告信息
        om.MGlobal.displayWarning(warning_message)
    #警告打印
    def mayaWarn(self ,warning_message):
        om.MGlobal.displayWarning(warning_message)
    #maya视窗口打印
    def mayaViewMessage(self , message ,fade = True):
        cmds.inViewMessage(amg=message, pos='topCenter', fade=fade)

printTool = MayaPrint()