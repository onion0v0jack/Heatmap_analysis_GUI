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
        self.setWindowTitle('熱圖分析 ver 1.1')
        self.setWindowIcon(QIcon("favicon.ico"))
        self.resize(QSize(1500, 800))

        #【設定UI中的元件】
        # 按鍵顯示
        self.btn_upload_csv = QPushButton('載入csv資料')
        self.btn_start = QPushButton('開始')
        # 字元顯示
        self.label_maintitle = QLabel('射出機熱圖分析')
        self.label_upload_filename = QLabel()    # 如果一開始沒有要設定內容，可直接設定初始為空白
        self.label_message = QLabel()
        # self.version_number = QLabel('V1.1')

        # 捲動區域顯示
        ## 設定捲動區域
        scroll_layout = QVBoxLayout()  #先建立一個直列空區塊
        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_layout)
        self.scroll_box = QScrollArea() # 建立捲動區域，並將scroll_widget設置其中
        self.scroll_box.setWidgetResizable(True)  # 設置是否自動調整部件大小(必須要True)
        self.scroll_box.setWidget(scroll_widget)
        # self.scroll_box.setFixedHeight(200) # 固定捲動區域的高度
        ## 新增選項列，預設為空
        self.checkbox_list = []
        ## 建立QGroupBox，內部為直列，之後用self.scroll_box包
        self.groupBox = QGroupBox() 
        self.checkBox = QVBoxLayout()         
        self.groupBox.setLayout(self.checkBox)
        self.groupBox.setFlat(False) # True:很像分隔線；False:區塊分隔
        scroll_layout.addWidget(self.groupBox)

        # 日曆顯示
        self.calender_date = QCalendarWidget()
        # 表格顯示
        self.table_IDATA = QTableView()
        self.table_CV = QTableView()
        self.table_message = QTableView()
        self.df_message = pd.DataFrame(columns = ['index', 'catch_sn', 'message'])
        self.table_message.setModel(pandasModel(self.df_message))
        # 圖片顯示
        self.plot_output_result = MplWidget()
        self.plot_cluster = MplWidget()
        # 分頁顯示
        self.tabs_setting = QTabWidget()
        self.tabs_result = QTabWidget()
        self.tabs_plot = QTabWidget()   
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        

        ### 字型設定
        self.label_maintitle.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 15pt; font-weight: bold;}")
        self.label_upload_filename.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 8pt; border: 1px solid black;}")
        self.label_message.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 10pt; border: 1px solid black;}")
        self.label_upload_filename.setWordWrap(True) # 自動換行
        self.label_message.setWordWrap(True) 
        self.label_maintitle.setFixedHeight(30)  # 固定高度
        self.label_upload_filename.setFixedHeight(60)
        ### 選單區域文字設定
        self.groupBox.setStyleSheet("QGroupBox{font-family: Microsoft JhengHei; font-weight: bold;}")
        ### 按鍵字元設定
        self.btn_upload_csv.setStyleSheet("QPushButton{font-family: Microsoft JhengHei; font-size: 10pt;}")
        self.btn_start.setStyleSheet("QPushButton{font-family: Microsoft JhengHei; font-size: 10pt;}")
        self.btn_upload_csv.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_start.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        ### 日曆設定
        self.calender_date.setGridVisible(True)
        # self.calender_date.setFixedHeight(250)
        self.calender_date.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        ### 表格大小設定
        self.table_IDATA.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # 把顯示表格的寬調整到最小
        self.table_CV.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) 
        self.table_message.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) 
        self.table_IDATA.setFixedHeight(175)
        ### 圖片大小設定
        # self.plot_output_result.setMinimumHeight(550)
        ### 分頁設定
        self.tabs_setting.setFixedHeight(250)
        self.tabs_setting.addTab(self.calender_date, '日期設定')
        self.tabs_setting.addTab(self.scroll_box, '欄位設定')
        self.tabs_setting.setStyleSheet("QTabWidget{font-family: Microsoft JhengHei; font-size: 9pt;}")

        self.tabs_result.setFixedHeight(175)
        self.tabs_result.addTab(self.table_CV, '變異係數')
        self.tabs_result.addTab(self.table_message, '警示/建議')
        self.tabs_result.setStyleSheet("QTabWidget{font-family: Microsoft JhengHei; font-size: 9pt;}")

        self.tabs_plot.setMinimumHeight(550)
        self.tabs_plot.addTab(self.plot_output_result, '熱圖/前後差異指數')
        self.tabs_plot.addTab(self.plot_cluster, '模次分類圖')
        self.tabs_plot.setStyleSheet("QTabWidget{font-family: Microsoft JhengHei; font-size: 9pt;}")


        #【設定佈局(layout)】
        # main layout
        layout = QVBoxLayout()   # 建立layout，最初指定垂直切分。layout之後要定義一個widget讓layout設定進去(註*1)
        #################################
        #### up layout ####     # 分左右，左邊為主要設定，右邊為顯示圖，左:右 = 2:7
        up_layout = QHBoxLayout() 

        setting_layout = QVBoxLayout()
        setting_layout.addWidget(self.label_maintitle)  # 建立layout之後就可以塞元件了
        setting_layout.addWidget(self.btn_upload_csv)
        setting_layout.addWidget(self.label_upload_filename)
        setting_layout.addWidget(self.tabs_setting)
        setting_layout.addWidget(self.btn_start)
        setting_layout.addWidget(self.label_message)
        setting_widget = QWidget()
        setting_widget.setLayout(setting_layout)

        up_layout.addWidget(setting_widget) 
        up_layout.addWidget(self.tabs_plot)
        up_layout.setStretchFactor(setting_widget, 2) 
        up_layout.setStretchFactor(self.tabs_plot, 7)
        up_widget = QWidget()
        up_widget.setLayout(up_layout)
        #### down layout ####     # 分左右，左:右 = 7:3
        down_layout = QHBoxLayout() 
        down_layout.addWidget(self.table_IDATA)
        down_layout.addWidget(self.tabs_result)
        down_layout.setStretchFactor(self.table_IDATA, 7) 
        down_layout.setStretchFactor(self.tabs_result, 3) 
        down_widget = QWidget()
        down_widget.setLayout(down_layout)

        layout.addWidget(up_widget)
        layout.addWidget(down_widget)
        #################################
        main_widget = QWidget()                       # (註*1)每一次建layout後要用widget包
        main_widget.setLayout(layout)                 # (註*1)每一次建layout後要用widget包
        self.setCentralWidget(main_widget)            # 設定main_widget為中心視窗

        #【設定button觸發的slot(function)】
        self.btn_upload_csv.clicked.connect(self.upload_data_slot)
        self.btn_start.clicked.connect(self.slot_press_start)

        # 【設定全域變數】
        self.column_index_eng_dict = {
            0: 'daTemp_MeltRealN',
            1: 'daTemp_MeltReal1',
            2: 'daTemp_MeltReal2',
            3: 'daTemp_MeltReal3',
            4: 'daTemp_MeltReal4',
            5: 'daTemp_MeltReal5',
            6: 'daTemp_MeltRealIn',
            8: 'daTemp_MoldReal1',
            9: 'daTemp_MoldReal2',
            10: 'adPosi_VP',
            11: 'adPosi_End',
            12: 'adPosi_InjectStart',
            14: 'daRo_MeteringRpm1',
            15: 'daRo_MeteringRpm2',
            16: 'daRo_MeteringRpm3',
            18: 'daPres_InjectAvg',
            19: 'daPres_Hold1',
            20: 'daPres_Hold2',
            21: 'daPres_Hold3',
            22: 'daPres_Hold4',
            23: 'daPres_Hold5',
            24: 'daPres_BackPressure1',
            25: 'daPres_BackPressure2',
            26: 'daPres_BackPressure3',
            28: 'daVelo_Inject1',
            29: 'daVelo_Inject2',
            30: 'daVelo_Inject3',
            31: 'daVelo_Inject4',
            32: 'daVelo_Inject5',
            33: 'daVelo_Inject6',
            34: 'daPres_Inject1',
            35: 'daPres_Inject2',
            36: 'daPres_Inject3',
            37: 'daPres_Inject4',
            38: 'daPres_Inject5',
            39: 'daPres_Inject6',
            48: 'tm_Cycle',
            49: 'tm_Inject',
            50: 'tm_Metering',
            51: 'adPosi_MeteringStart',
            52: 'daMet_InjectEnd',
            53: 'daMet_End',
            57: 'daMet_HoldEnd',
            59: 'daPres_Max',
            60: 'daVelo_Max',
            61: 'adPosi_HoldEnd',
        }
        self.column_eng_chinese_dict = {
            'daTemp_MeltRealN': '溫度實際值 射嘴',
            'daTemp_MeltReal1': '溫度實際值 1',
            'daTemp_MeltReal2': '溫度實際值 2',
            'daTemp_MeltReal3': '溫度實際值 3',
            'daTemp_MeltReal4': '溫度實際值 4',
            'daTemp_MeltReal5': '溫度實際值 5',
            'daTemp_MeltRealIn': '溫度實際值 入料',
            'daTemp_MoldReal1': '模溫實際值 1*',
            'daTemp_MoldReal2': '模溫實際值 2*',
            'adPosi_VP': '保壓轉換位置',
            'adPosi_End': '餘量位置',
            'adPosi_InjectStart': '射出起點',
            'daRo_MeteringRpm1': '儲料1段迴轉速',
            'daRo_MeteringRpm2': '儲料2段迴轉速',
            'daRo_MeteringRpm3': '儲料3段迴轉速',
            'daPres_InjectAvg': '最大射出壓力',
            'daPres_Hold1': '保壓1段壓力',
            'daPres_Hold2': '保壓2段壓力',
            'daPres_Hold3': '保壓3段壓力',
            'daPres_Hold4': '保壓4段壓力',
            'daPres_Hold5': '保壓5段壓力',
            'daPres_BackPressure1': '儲料1段背壓壓力',
            'daPres_BackPressure2': '儲料2段背壓壓力',
            'daPres_BackPressure3': '儲料3段背壓壓力',
            'daVelo_Inject1': '射出1段速度',
            'daVelo_Inject2': '射出2段速度',
            'daVelo_Inject3': '射出3段速度',
            'daVelo_Inject4': '射出4段速度',
            'daVelo_Inject5': '射出5段速度',
            'daVelo_Inject6': '射出6段速度',
            'daPres_Inject1': '射出1段壓力',
            'daPres_Inject2': '射出2段壓力',
            'daPres_Inject3': '射出3段壓力',
            'daPres_Inject4': '射出4段壓力',
            'daPres_Inject5': '射出5段壓力',
            'daPres_Inject6': '射出6段壓力',
            'tm_Cycle': '循環時間',
            'tm_Inject': '射出計時',
            'tm_Metering': '儲料計時',
            'adPosi_MeteringStart': '加料開始位置',
            'daMet_InjectEnd': '劑量(射出結束)',
            'daMet_End': '劑量(結束)',
            'daMet_HoldEnd': '劑量(保壓結束)',
            'daPres_Max': '平均射出壓力',
            'daVelo_Max': '最大射出速度',
            'adPosi_HoldEnd': '保壓終了位置',
        }
        self.filename = None
        self.date = None
        self.input_data = None
        self.cluster_array = None
        
        ### thread
        self.th1_work, self.th2_work = None, None

        # 【checkbox讀取欄位，內部選項需都設定好】
        self.add_checkbox()   
    
    def add_checkbox(self):
        for key in self.column_index_eng_dict:
            tempCheckBox = QCheckBox("{}({})".format(self.column_index_eng_dict[key], self.column_eng_chinese_dict[self.column_index_eng_dict[key]]))
            tempCheckBox.setChecked(True)
            tempCheckBox.setStyleSheet("QCheckBox{font-family: Microsoft JhengHei}")
            self.checkbox_list.append(tempCheckBox)
            self.checkBox.addWidget(tempCheckBox)

    def upload_data_slot(self):
        """Slot of uploading data (with btn_upload_csv)"""
        file, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Data Files (*.csv)")  # 建立開啟檔案的對話盒(dialog)
        if file:
            self.filename = file
            self.label_upload_filename.setText(file)                 # 將label_upload_filename複寫為檔名(file)


    def slot_press_start(self):
        self.show_column_list = []
        for checkbox in self.checkbox_list:
            if checkbox.isChecked():
                self.show_column_list.append(checkbox.text().split('(')[0])
        print(self.show_column_list)
        self.date = self.calender_date.selectedDate().toString('yyyy-MM-dd')
        if self.filename == None:
            self.label_message.setText('請選擇載入檔案')
        else:
            # print(self.date)
            # print(self.filename)
            self.th1_work = WorkThread(self.date, self.filename, self.show_column_list, self.df_message)
            self.th1_work.start()
            self.th1_work.signal_data_table.connect(self.slot_show_table)
            self.th1_work.signal_data_table_cv.connect(self.slot_show_table_cv)
            self.th1_work.signal_action.connect(self.slot_message)  
            self.th1_work.signal_data_message_update.connect(self.slot_update_df_message)  
            self.th1_work.signal_data_list_for_plot.connect(self.slot_prepare_for_plot)  
            
    def slot_show_table(self, data_df):
        self.table_IDATA.setModel(pandasModel(data_df))
        self.input_data = data_df
    
    def slot_show_table_cv(self, data_df):
        self.table_CV.setModel(pandasModel(data_df))
    
    def slot_message(self, message_str):
        self.label_message.setText(message_str) 
    
    def slot_update_df_message(self, data_df):
        self.table_message.setModel(pandasModel(data_df))
    
    def slot_prepare_for_plot(self, data_list):
        self.label_message.setText('計算中...')
        data_arg, data_distrance, self.cluster_array = data_list
        DMDA = data_distrance.mean().diff().abs()

        self.th2_work = WorkThread_plot(self.date, data_arg, data_distrance, DMDA, self.cluster_array, self.plot_output_result, self.plot_cluster)
        self.th2_work.start()
        self.th2_work.signal_plot_result.connect(self.slot_draw_plot_result)
        self.th2_work.signal_plot_cluster.connect(self.slot_draw_plot_cluster)
        self.label_message.setText('繪圖完成')

    def slot_draw_plot_result(self, object):
        self.plot_output_result = object
    
    def slot_draw_plot_cluster(self, object):
        self.plot_cluster = object


def main():
    app = QApplication([])
    app.setStyle(QStyleFactory.create('fusion'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()