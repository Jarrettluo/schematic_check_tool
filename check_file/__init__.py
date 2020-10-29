# encoding: utf-8
"""
@version: 1.0
@author: Jarrett
@file: __init__.py
@time: 2020/10/28 13:53
"""
from PyQt5.QtCore import QThread, pyqtSignal
from .perform_check import check

class CheckFiles(QThread):
    signal = pyqtSignal(list)  # 括号里填写信号传递的参数

    def __init__(self, args_list):
        super().__init__()
        self.args_data = args_list

    def __del__(self):
        self.wait()

    def run(self):
        # 进行任务操作
        try:
            df1, df2 = check(self.args_data[0][-1], self.args_data[1][-1])
            value = [df1, df2]
            self.signal.emit(value)  # 发射信号
        except Exception as e:
            print(e)