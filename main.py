# encoding: utf-8
"""
@version: 1.0
@author: Jarrett
@file: main
@time: 2020/10/21 13:57
"""

import os
import sys
import time
"""
以下引用是由于使用PyInstaller进行软件打包时出现bug。
参考链接：https://bbs.csdn.net/topics/392428917
"""
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor
from check_file import CheckFiles
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMenu, QAction, QTreeWidgetItem, QHeaderView, QDirModel, \
    QTreeView, QFileDialog, QTableWidgetItem


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("ui_source/main.ui", self)

        self.setWindowTitle("网线检查工具  润科通用开发")

        self.check_rules = []  # 初始化检查规则文件，首先置空
        self.nets_files = []  # 初始化网表文件，首先置空
        self.result_files = []  # 初始化结果文件，置空！

        self.pushButton_new.setIcon(QIcon("ui_source/icon_new.png"))
        self.pushButton_save.setIcon(QIcon("ui_source/icon_save.png"))
        self.pushButton_start.setIcon(QIcon("ui_source/icon_start.png"))
        self.pushButton_export.setIcon(QIcon("ui_source/icon_export.png"))

        self.pushButton_new.clicked.connect(self.new_project)  # 点击新建按钮
        self.pushButton_save.clicked.connect(self.save_project)  # 点击保存按钮
        self.pushButton_start.clicked.connect(self.start_check)  # 点击检查按钮
        self.pushButton_export.clicked.connect(self.export_result)  # 点击导出按钮

        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderLabels(['检查工程'])
        # 设置自适应宽度
        # self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        rule_group = QTreeWidgetItem(self.treeWidget)
        rule_group.setText(0, '检查规则')
        file_group = QTreeWidgetItem(self.treeWidget)
        file_group.setText(0, '检查文件')

        result_group = QTreeWidgetItem(self.treeWidget)
        result_group.setText(0, '检查结果')

        self.treeWidget.expandAll()  # 打开全部
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # 打开右键菜单的策略
        self.treeWidget.customContextMenuRequested.connect(self.treeWidgetItem_fun)  # 绑定事件


        self.tableWidget_2.horizontalHeader().resizeSection(0, 150)
        # self.tableWidget_2.horizontalHeader().resizeSection(1, 550)
        self.tableWidget_2.setColumnCount(2)
        self.tableWidget_2.setHorizontalHeaderLabels(['元器件', '管脚未引出'])



    # 项目管理窗口右键功能选项
    def treeWidgetItem_fun(self, pos):
        item = self.treeWidget.currentItem()
        item1 = self.treeWidget.itemAt(pos)
        if item.parent() == None and item.text(0) != "检查结果":
            popMenu = QMenu()
            new_action = QAction(QIcon("ui_source/net_file.png"), "新建", popMenu)
            # new_action.triggered.connect(lambda: print("新建")) // 暂时屏蔽，无法使用
            import_action = QAction(QIcon("ui_source/net_file.png"), "导入", popMenu)
            import_action.triggered.connect(lambda: self.rule_file_dialog(item.text(0)))
            clear_action = QAction(u"清空", popMenu)
            clear_action.triggered.connect(lambda: self.clear_all_child(item))
            popMenu.addAction(new_action)
            popMenu.addAction(import_action)
            popMenu.addSeparator()  # 添加分隔线
            popMenu.addAction(clear_action)
            # popMenu.triggered[QAction].connect(self.processtrigger) # 暂时屏蔽
            popMenu.exec_(QCursor.pos())
        else:
            if item.text(0) != "检查结果":
                popMenu = QMenu()
                delete_action = QAction(u"删除", popMenu)
                delete_action.triggered.connect(lambda: self.delete_item(item))
                popMenu.addAction(delete_action)
                # popMenu.triggered[QAction].connect(self.processtrigger) # 暂时屏蔽
                popMenu.exec_(QCursor.pos())

    # 导入文件窗口
    def rule_file_dialog(self, msg):
        fileName1, filetype = QFileDialog.getOpenFileName(self, "选取文件", "./",
                                                          "Text Files ();;All Files (*)")  # 设置文件扩展名过滤,注意用双分号间隔
        if fileName1:
            file_path_list = fileName1.split('/')[0:-1]  # 获取文件路径
            filename = fileName1.split('/')[-1]
            self.file_path = '/'.join(file_path_list)
            if msg == "检查文件":
                aa = self.treeWidget.topLevelItem(1)
                file1 = QTreeWidgetItem(aa)
                file1.setText(0, filename)
                file1.setIcon(0, QIcon("ui_source/net_file.png"))
                self.nets_files.append(fileName1)
            else:
                aa = self.treeWidget.topLevelItem(0)
                rule1 = QTreeWidgetItem(aa)
                rule1.setText(0, filename)
                rule1.setIcon(0, QIcon("ui_source/checklist.png"))
                self.check_rules.append(fileName1)
        else:
            pass

    def clear_all_child(self, item):
        """
        清空子节点
        :param item:
        :return:
        """
        # item 为当前父节点
        for i in range(item.childCount()):
            item.removeChild(item.child(0))
        pass

    # 删除一个子节点
    def delete_item(self, item):
        """
        :param item:
        :return:
        """
        print("删除子子节点")
        parent = item.parent()  # 获取父节点
        parent.removeChild(item)  # 删除子节点

    def export_result(self):
        print("导出结果")

    def start_check(self):
        print("开始检查")
        if len(self.check_rules) >0 and len(self.nets_files)>0:
            self.pushButton_start.setIcon(QIcon("ui_source/icon_stop.png"))
            self.pushButton_start.setEnabled(False)
            args_list = [self.check_rules, self.nets_files]  # 这里进行检查的线程操作
            self.check_thread = CheckFiles(args_list)
            self.check_thread.signal.connect(self.check_callback)
            self.check_thread.start()  # 启动线程

    # 检查后执行的回调函数
    def check_callback(self, value):
        df1 = value[0]
        df2 = value[1]
        if df1.empty == False:
            i = 0
            self.tableWidget.setRowCount(df1.shape[0])
            self.tableWidget.setColumnCount(2)
            self.tableWidget.setColumnCount(6)
            self.tableWidget.horizontalHeader().resizeSection(0, 120)
            self.tableWidget.horizontalHeader().resizeSection(1, 270)
            self.tableWidget.horizontalHeader().resizeSection(2, 120)
            self.tableWidget.horizontalHeader().resizeSection(3, 120)
            self.tableWidget.horizontalHeader().resizeSection(4, 120)
            self.tableWidget.horizontalHeader().resizeSection(5, 120)
            self.tableWidget.setHorizontalHeaderLabels(['网线', '元器件', '电源和GND管脚特性检查',
                                                        '管脚上下拉配置检查', '差分网络极性检查',
                                                        '电容耐压值降额检查'])
            for indexs in df1.index:
                print(indexs)
                newItem = QTableWidgetItem(str(indexs))
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(i, 0, newItem)
                newItem = QTableWidgetItem(str(df1.loc[indexs].values[0]))
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(i, 1, newItem)
                i+=1
            self.tableWidget.resizeRowsToContents()

        if df2.empty == False:
            i = 0
            self.tableWidget_2.setRowCount(df2.shape[0])
            self.tableWidget_2.setColumnCount(2)
            for indexs in df2.index:
                print(indexs)
                newItem = QTableWidgetItem(str(indexs))
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget_2.setItem(i, 0, newItem)
                newItem = QTableWidgetItem(str(df2.loc[indexs].values[0]))
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget_2.setItem(i, 1, newItem)
                i+=1
        self.pushButton_start.setIcon(QIcon("ui_source/icon_start.png"))
        self.pushButton_start.setEnabled(True)
        now_time = time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(time.time()))
        aa = self.treeWidget.topLevelItem(2)
        file1 = QTreeWidgetItem(aa)
        file1.setText(0, f"result_{now_time}")
        file1.setIcon(0, QIcon("ui_source/net_file.png"))



    def new_project(self):
        print("新建工程")

    def save_project(self):
        print("保存工程")

    def whichBtn(self, btn):
        print("点击的按钮是：", btn.text())


class myMenu(QTreeWidgetItem):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.setContextMenuPolicy(Qt.CustomContextMenu)  # 打开右键菜单的策略
        self.customContextMenuRequested.connect(self.rightClickMenu)  # 绑定事件

    def rightClickMenu(self, pos):
        try:
            self.contextMenu = QMenu()  # 创建对象
            self.actionA = self.contextMenu.addAction(u'动作')  # 添加动作
            self.actionA = self.contextMenu.addAction(u'动作b')
            self.actionA.triggered.connect(self.actionHandler)
            self.contextMenu.exec_(self.mapToGlobal(pos))  # 随指针的位置显示菜单
            self.contextMenu.show()  # 显示
        except Exception as e:
            print(e)

    def actionHandler(self):
        print(self.currentItem().text(0))


class MyLabel(QLabel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightMenuShow)  # 开放右键策略

    def rightMenuShow(self, pos):  # 添加右键菜单
        menu = QMenu(self)
        menu.addAction(QAction('添加规则文件', menu))
        menu.addAction(QAction('动作2', menu))
        menu.addAction(QAction('动作3', menu))
        menu.triggered.connect(self.menuSlot)
        menu.exec_(QCursor.pos())

    def menuSlot(self, act):
        print(act.text())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    with open('./style_source/app_style.qss', encoding='utf-8') as f:
        qss_style = f.read()
    window.setStyleSheet(qss_style)
    window.show()
    sys.exit(app.exec_())
