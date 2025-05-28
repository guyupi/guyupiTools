#!/usr/bin/python
#encoding:gbk
import maya.cmds as cmds
import mayaPrint
import time

class ProgressWin(object):
    def __init__(self, num, label=None, return_result=True):
        self.__num = num
        self.__label = label
        # self.__progress = 0
        self.__status = None
        self.__timeStart = None
        self.__timeEnd = None
        self._return = return_result
        if self.__num <= 100:
            self.__times = 1
            self.__frames = self.__num / 100.0
        else:
            self.__times = self.__num / 100
            self.__frames = self.__num / 100
    @ property
    def status(self):
        return self.__status

    @ status.setter
    def status(self, value):
        self.__status = value
    def __enter__(self):
        # ... distinct the passing parameter whether a list or not
        if not isinstance(self.__num, int):
            raise ValueError('please pass a integer value to configure where the progress window goes')

        # ... open maya progress window and set the progressing
        if self.__label is None:
            self.__label = 'retrieval...'
        self.__timeStart = time.time()
        # ... start the window

        cmds.progressWindow(title=self.__label)
        return self

    def edit_window(self, value, text=None):
        if text is None:
            text = self.__status
        if value / self.__times > 0 and value % self.__times == 0:
            pr = value / self.__frames
            # ... attention : cause the status settings waste too much time, so 尽量别去设置status属性
            cmds.progressWindow(e=1, pr=pr, status=text)

    def __exit__(self, *exc_info):
        self.__timeEnd = time.time()
        cmds.progressWindow(endProgress=True)
        if self._return:
            mayaPrint.printTool.mayaPrint('{} Totally takes around {} Seconds.'.format(self.__label, self.__timeEnd - self.__timeStart))

