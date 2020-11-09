# 版本號： ver 1.0
import datetime
import itertools
import os
import random
import sys
import warnings
import pandas as pd
from mplWidget import MplWidget
from pandasModel import pandasModel
from PySide2 import QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from thread import *

warnings.filterwarnings("ignore") # 要求忽略warning
import matplotlib.pyplot as plt
plt.style.use('ggplot')   # 設定畫圖風格為ggplot
plt.rcParams['font.sans-serif'] = ['SimHei'] # 設定相容中文 
plt.rcParams['axes.unicode_minus'] = False
pd.options.mode.chained_assignment = None

QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))  # 掃plugin套件(windows必備)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #【設定初始化，UI標題與視窗大小】
        self.setWindowTitle('熱圖分析 ver 1.0')
        self.setWindowIcon(QIcon("favicon.ico"))
        self.resize(QSize(1500, 700))

        #【設定UI中的元件】
        # 按鍵顯示
        self.btn_upload_csv = QPushButton('載入csv資料')
        self.btn_start = QPushButton('開始')
        # 字元顯示
        self.label_maintitle = QLabel('射出機熱圖分析')
        self.label_upload_filename = QLabel()    # 如果一開始沒有要設定內容，可直接設定初始為空白
        self.label_setting_date = QLabel('選擇日期') 
        self.label_message = QLabel('')
        # self.version_number = QLabel('V1.0')
        # 日曆顯示
        self.calender_date = QCalendarWidget()
        # 表格顯示
        self.table_IDATA = QTableView()
        # 圖片顯示
        self.plot_output_result = MplWidget()

        ### 字型設定
        self.label_maintitle.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 15pt; font-weight: bold;}")
        self.label_upload_filename.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 9pt; border: 1px solid black;}")
        self.label_setting_date.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 12pt; font-weight: bold;}")
        self.label_message.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 10pt; border: 1px solid black;}")
        self.label_upload_filename.setWordWrap(True) # 自動換行
        self.label_message.setWordWrap(True) 
        self.label_maintitle.setFixedHeight(40)  # 固定高度
        self.label_upload_filename.setFixedHeight(80)
        self.label_setting_date.setFixedHeight(40)
        ### 按鍵字元設定
        self.btn_upload_csv.setStyleSheet("QPushButton{font-family: Microsoft JhengHei; font-size: 10pt;}")
        self.btn_start.setStyleSheet("QPushButton{font-family: Microsoft JhengHei; font-size: 10pt;}")
        self.btn_upload_csv.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_start.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        ### 日曆設定
        self.calender_date.setGridVisible(True)
        self.calender_date.setFixedHeight(250)
        self.calender_date.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        ### 表格大小設定
        self.table_IDATA.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # 把顯示表格的寬調整到最小

        self.table_IDATA.setFixedHeight(150)
        ### 圖片大小設定
        self.plot_output_result.setMinimumHeight(550)

        #【設定佈局(layout)】
        # main layout
        layout = QHBoxLayout() # 建立layout並指定layout為水平切分 # 建立layout之後要定義一個widget讓layout設定進去(註*1)
        
        # left layout
        left_layout = QVBoxLayout()                  # 設定此layout為垂直切分
        left_layout.addWidget(self.label_maintitle)  # 建立layout之後就可以塞元件了
        left_layout.addWidget(self.btn_upload_csv)
        left_layout.addWidget(self.label_upload_filename)
        left_layout.addWidget(self.label_setting_date)
        left_layout.addWidget(self.calender_date)
        left_layout.addWidget(self.btn_start)
        left_layout.addWidget(self.label_message)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)           # 建立left layout的widget(參考main layout的註*1)

        # right layout
        right_layout = QVBoxLayout() 
        right_layout.addWidget(self.plot_output_result)
        right_layout.addWidget(self.table_IDATA)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)               # 建立right layout的widget
        
        layout.addWidget(left_widget)                 # 設定好left與right layout的widget之後加入在main layout
        layout.addWidget(right_widget)
        layout.setStretchFactor(left_widget, 1)       # 設定left_widget與right_widget的比例
        layout.setStretchFactor(right_widget, 5) 
        main_widget = QWidget()                       # (註*1)每一次建layout後要用widget包
        main_widget.setLayout(layout)                 # (註*1)每一次建layout後要用widget包
        self.setCentralWidget(main_widget)            # 設定main_widget為中心視窗

        #【設定button觸發的slot(function)】
        self.btn_upload_csv.clicked.connect(self.upload_data_slot)
        self.btn_start.clicked.connect(self.slot_press_start)

        # 【設定全域變數】
        self.filename = None
        self.date = None
        self.input_data = None
        ### thread
        self.th1_work = None
        self.th2_work = None
    
    def upload_data_slot(self):
        """Slot of uploading data (with btn_upload_csv)"""
        file, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Data Files (*.csv)")  # 建立開啟檔案的對話盒(dialog)
        if file:
            self.filename = file
            self.label_upload_filename.setText(file)                 # 將label_upload_filename複寫為檔名(file)

    def slot_press_start(self):
        self.date = self.calender_date.selectedDate().toString('yyyy-MM-dd')
        if self.filename == None:
            self.label_message.setText('請選擇載入檔案')
        else:
            print(self.date)
            print(self.filename)
            self.th1_work = WorkThread(self.date, self.filename)
            self.th1_work.start()
            self.th1_work.signal_data_table.connect(self.slot_show_table)
            self.th1_work.signal_action.connect(self.slot_message)  
            self.th1_work.signal_data_list_for_plot.connect(self.slot_prepare_for_plot)  
            
    def slot_show_table(self, data_df):
        self.table_IDATA.setModel(pandasModel(data_df))
        self.input_data = data_df
    
    def slot_message(self, message_str):
        self.label_message.setText(message_str) 
    
    def slot_prepare_for_plot(self, data_list):
        self.label_message.setText('計算中...')
        data_arg, data_distrance = data_list
        DMDA = data_distrance.mean().diff().abs()

        self.th2_work = WorkThread_plot(self.date, data_arg, data_distrance, DMDA, self.plot_output_result)
        self.th2_work.start()
        self.th2_work.signal_plot.connect(self.slot_draw_plot)
        self.label_message.setText('繪圖完成')
    
    def slot_draw_plot(self, object):
        self.plot_output_result = object


def main():
    app = QApplication([])
    app.setStyle(QStyleFactory.create('fusion'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()