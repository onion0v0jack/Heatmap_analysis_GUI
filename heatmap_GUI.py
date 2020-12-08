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
        self.setWindowTitle('熱圖分析 ver 1.2')
        self.setWindowIcon(QIcon("favicon.ico"))
        self.resize(QSize(1500, 800))

        #【新增UI中的顯示元件】
        # ● 按鍵
        self.btn_upload_csv = QPushButton('載入csv資料')
        self.btn_start = QPushButton('開始')
        # ● 字元 (一開始如不設定內容，初始可空白)
        self.label_maintitle = QLabel('射出機熱圖分析')
        self.label_upload_filename = QLabel()
        self.label_message = QLabel()
        self.label_DBSCAN = QLabel('DBSCAN')
        self.label_DBSCAN1 = QLabel('Epsilon')
        self.label_DBSCAN2 = QLabel('Min_samples')
        self.label_sigma_filter = QLabel('前後差異指數篩選標準參數')
        self.label_sigma_alpha = QLabel('alpha (0~0.5)')
        self.label_sigma_k = QLabel('k(>0)')
        self.label_suggest = QLabel()
        # self.version_number = QLabel('V1.2')

        # ● 輸入欄位 (因之後會放在分頁裡，所以先完成layput)
        self.edit_DBSCAN1 = QLineEdit('11')
        self.edit_DBSCAN2 = QLineEdit('9')
        self.edit_sigma_alpha = QLineEdit('0.35')
        self.edit_sigma_k = QLineEdit('3')
        parameter_layout = QVBoxLayout()

        DBSCAN1_layout = QHBoxLayout() 
        DBSCAN1_layout.addWidget(self.label_DBSCAN1)
        DBSCAN1_layout.addWidget(self.edit_DBSCAN1)
        DBSCAN1_layout.setStretchFactor(self.label_DBSCAN1, 2)   #比例調整
        DBSCAN1_layout.setStretchFactor(self.edit_DBSCAN1, 3)    #比例調整
        DBSCAN1_widget = QWidget()
        DBSCAN1_widget.setLayout(DBSCAN1_layout)

        DBSCAN2_layout = QHBoxLayout() 
        DBSCAN2_layout.addWidget(self.label_DBSCAN2)
        DBSCAN2_layout.addWidget(self.edit_DBSCAN2)
        DBSCAN2_layout.setStretchFactor(self.label_DBSCAN2, 2) 
        DBSCAN2_layout.setStretchFactor(self.edit_DBSCAN2, 3) 
        DBSCAN2_widget = QWidget()
        DBSCAN2_widget.setLayout(DBSCAN2_layout)

        sigma1_layout = QHBoxLayout() 
        sigma1_layout.addWidget(self.label_sigma_alpha)
        sigma1_layout.addWidget(self.edit_sigma_alpha)
        sigma1_layout.setStretchFactor(self.label_sigma_alpha, 2) 
        sigma1_layout.setStretchFactor(self.edit_sigma_alpha, 3) 
        sigma1_widget = QWidget()
        sigma1_widget.setLayout(sigma1_layout)

        sigma2_layout = QHBoxLayout() 
        sigma2_layout.addWidget(self.label_sigma_k)
        sigma2_layout.addWidget(self.edit_sigma_k)
        sigma2_layout.setStretchFactor(self.label_sigma_k, 2) 
        sigma2_layout.setStretchFactor(self.edit_sigma_k, 3) 
        sigma2_widget = QWidget()
        sigma2_widget.setLayout(sigma2_layout)

        parameter_layout.addWidget(self.label_DBSCAN)
        parameter_layout.addWidget(DBSCAN1_widget)
        parameter_layout.addWidget(DBSCAN2_widget)
        parameter_layout.addWidget(self.label_sigma_filter)
        parameter_layout.addWidget(sigma1_widget)
        parameter_layout.addWidget(sigma2_widget)
        parameter_widget = QWidget()
        parameter_widget.setLayout(parameter_layout)

        # ● 捲動區域
        ## 設定捲動區域
        self.scroll_box = QScrollArea() # 建立捲動區域，並將scroll_widget設置其中
        self.scroll_box.setWidgetResizable(True)  # 設置是否自動調整部件大小(必須要True)
        self.groupBox = QGroupBox() 
        self.checkBox = QVBoxLayout()         
        self.groupBox.setLayout(self.checkBox)
        self.scroll_box.setWidget(self.groupBox) 

        self.scroll_suggest = QScrollArea() # 建立捲動區域，並將scroll_widget設置其中
        self.scroll_suggest.setWidgetResizable(True)  # 設置是否自動調整部件大小(必須要True)
        self.scroll_suggest.setWidget(self.label_suggest)

        self.scroll_parameter = QScrollArea()
        self.scroll_parameter.setWidgetResizable(True)
        self.scroll_parameter.setWidget(parameter_widget)

        # ● 日曆
        self.calender_date = QCalendarWidget()
        # ● 表格
        self.table_IDATA = QTableView()
        self.table_CV = QTableView()
        self.table_error_log = QTableView()
        self.table_message = QTableView()
        self.df_message = pd.DataFrame(columns = ['index', 'catch_sn', 'message'])
        self.table_message.setModel(pandasModel(self.df_message))
        # ● 圖片
        self.plot_output_result = MplWidget()
        self.plot_cluster = MplWidget()
        # ● 分頁
        self.tabs_setting = QTabWidget()
        self.tabs_table1 = QTabWidget()
        self.tabs_table2 = QTabWidget()
        self.tabs_plot = QTabWidget()   
        # self.tab1 = QWidget()        

        #【設定元件】
        ### ● 字型
        self.label_maintitle.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 15pt; font-weight: bold;}")
        self.label_upload_filename.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 8pt; border: 1px solid black;}")
        self.label_message.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 10pt; border: 1px solid black;}")
        self.label_DBSCAN.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 10pt; font-weight: bold;}")
        self.label_DBSCAN1.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 9pt;}")
        self.label_DBSCAN2.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 9pt;}")
        self.label_sigma_filter.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 10pt; font-weight: bold;}")
        self.label_sigma_alpha.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 9pt;}")
        self.label_sigma_k.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 9pt;}")
        self.label_suggest.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 9pt;}")
        self.label_upload_filename.setWordWrap(True) # 自動換行
        self.label_message.setWordWrap(True)
        self.label_suggest.setWordWrap(True)
        self.label_maintitle.setFixedHeight(30)  # 固定高度
        self.label_upload_filename.setFixedHeight(60)
        ### ● 選單區域文字
        self.groupBox.setStyleSheet("QGroupBox{font-family: Microsoft JhengHei; font-weight: bold;}")
        ### ● 按鍵字元
        self.btn_upload_csv.setStyleSheet("QPushButton{font-family: Microsoft JhengHei; font-size: 10pt;}")
        self.btn_start.setStyleSheet("QPushButton{font-family: Microsoft JhengHei; font-size: 10pt;}")
        self.btn_upload_csv.setCursor(QCursor(QtCore.Qt.PointingHandCursor)) # 游標移過去時會變成手指
        self.btn_start.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        ### ● 日曆
        self.calender_date.setStyleSheet("QCalendarWidget{font-family: Microsoft JhengHei;}")
        self.calender_date.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.calender_date.setGridVisible(False) # 決定是否顯示格線
        ### ● 表格大小
        self.table_IDATA.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # 把顯示表格的寬調整到最小
        self.table_error_log.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_CV.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) 
        self.table_message.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) 
        ### ● 輸入欄位
        self.edit_DBSCAN1.setStyleSheet("QLineEdit{font-family: Microsoft JhengHei;}")
        self.edit_DBSCAN2.setStyleSheet("QLineEdit{font-family: Microsoft JhengHei;}")
        self.edit_sigma_alpha.setStyleSheet("QLineEdit{font-family: Microsoft JhengHei;}")
        self.edit_sigma_k.setStyleSheet("QLineEdit{font-family: Microsoft JhengHei;}")
        self.edit_DBSCAN1.setValidator(QDoubleValidator())  # 設定限定輸入字元形式，如整數Int、浮點數Double
        self.edit_DBSCAN2.setValidator(QIntValidator())
        self.edit_sigma_alpha.setValidator(QDoubleValidator())
        self.edit_sigma_k.setValidator(QDoubleValidator())
        ### ● 分頁 (先分配各分頁區塊)
        self.tabs_setting.addTab(self.calender_date, '日期設定')
        self.tabs_setting.addTab(self.scroll_box, '欄位設定')
        self.tabs_setting.addTab(self.scroll_parameter, '參數設定')
        
        self.tabs_table1.addTab(self.table_IDATA, '機台實際值資料')
        self.tabs_table1.addTab(self.table_message, '模次警示')
        self.tabs_table1.addTab(self.table_error_log, '模次異常欄位整理')
        
        self.tabs_table2.addTab(self.table_CV, '變異係數')
        self.tabs_table2.addTab(self.scroll_suggest, '建議')
        
        self.tabs_plot.addTab(self.plot_output_result, '熱圖/前後差異指數')
        self.tabs_plot.addTab(self.plot_cluster, '模次分類圖')
        
        self.tabs_setting.setFixedHeight(275)
        self.tabs_table1.setFixedHeight(175)
        self.tabs_table2.setFixedHeight(175)
        self.tabs_plot.setMinimumHeight(550)
        self.tabs_setting.setStyleSheet("QTabWidget{font-family: Microsoft JhengHei; font-size: 9pt;}")
        self.tabs_table1.setStyleSheet("QTabWidget{font-family: Microsoft JhengHei; font-size: 9pt;}")
        self.tabs_table2.setStyleSheet("QTabWidget{font-family: Microsoft JhengHei; font-size: 9pt;}")
        self.tabs_plot.setStyleSheet("QTabWidget{font-family: Microsoft JhengHei; font-size: 9pt;}")

        #【設定佈局(layout)】
        # main layout
        main_layout = QVBoxLayout()   # 建立layout，最初指定垂直切分。layout之後要定義一個widget讓layout設定進去(註*1)
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
        down_layout.addWidget(self.tabs_table1)
        down_layout.addWidget(self.tabs_table2)
        down_layout.setStretchFactor(self.tabs_table1, 7) 
        down_layout.setStretchFactor(self.tabs_table2, 3) 
        down_widget = QWidget()
        down_widget.setLayout(down_layout)

        main_layout.addWidget(up_widget)
        main_layout.addWidget(down_widget)
        #################################
        main_widget = QWidget()                       # (註*1)每一次建layout後要用widget包
        main_widget.setLayout(main_layout)            # (註*1)每一次建layout後要用widget包
        self.setCentralWidget(main_widget)            # 設定main_widget為中心視窗

        #【設定button觸發的slot(function)】
        self.btn_upload_csv.clicked.connect(self.slot_upload_data)
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
        self.data_error_log = pd.DataFrame()
        self.suggest_str = ''
        self.checkbox_list = []   ## 新增選項列，預設為空，給後台紀錄選項用
        self.th1_work, self.th2_work = None, None   ## thread

        # 【checkbox讀取欄位，內部選項需都設定好】
        self.add_checkbox()   
    
    def add_checkbox(self):
        # 將設定的欄位名稱寫入checkbox，另外全部存儲至self.checkbox_list
        for key in self.column_index_eng_dict:
            tempCheckBox = QCheckBox("{}({})".format(self.column_index_eng_dict[key], self.column_eng_chinese_dict[self.column_index_eng_dict[key]]))
            tempCheckBox.setChecked(True)
            tempCheckBox.setStyleSheet("QCheckBox{font-family: Microsoft JhengHei}")
            self.checkbox_list.append(tempCheckBox)
            self.checkBox.addWidget(tempCheckBox)

    def slot_upload_data(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Data Files (*.csv)")  # 建立對話盒(dialog)
        if file:
            self.filename = file
            self.label_upload_filename.setText(file) # 複寫label文字為檔名(file)

    def slot_press_start(self):
        self.show_column_list, self.suggest_str, self.date = [], '', self.calender_date.selectedDate().toString('yyyy-MM-dd')
        for checkbox in self.checkbox_list:  # 確認checkbox勾選狀態，將所選選項的英文部分存入self.show_column_list
            if checkbox.isChecked(): self.show_column_list.append(checkbox.text().split('(')[0])
        if self.filename == None:
            self.label_message.setText('請選擇載入檔案')
        elif (len(self.edit_DBSCAN1.text()) * len(self.edit_DBSCAN2.text()) * len(self.edit_sigma_alpha.text()) * len(self.edit_sigma_k.text())) == 0:
            self.label_message.setText('請確認參數是否確實設定')
        elif ((float(self.edit_sigma_alpha.text()) <= 0) | (float(self.edit_sigma_alpha.text()) >= 0.5) | (float(self.edit_sigma_k.text()) <= 0)):
            self.label_message.setText('請確認參數是否超出範圍')
        else:
            self.label_message.setText('計算中...')
            parameter_list = [float(self.edit_DBSCAN1.text()), int(self.edit_DBSCAN2.text()), float(self.edit_sigma_alpha.text()), float(self.edit_sigma_k.text())]
            self.th1_work = WorkThread(self.date, self.filename, self.show_column_list, self.df_message, parameter_list)
            self.th1_work.start()
            self.th1_work.signal_data_table_ori.connect(self.slot_show_table_ori)
            self.th1_work.signal_data_table_cv.connect(self.slot_show_table_cv)
            self.th1_work.signal_action.connect(self.slot_message)  
            self.th1_work.signal_data_message_update.connect(self.slot_update_df_message)  
            self.th1_work.signal_data_errorlog.connect(self.slot_update_df_errorlog)  
            self.th1_work.signal_data_list_for_plot.connect(self.slot_prepare_for_plot)
            
    def slot_show_table_ori(self, data_df):
        self.table_IDATA.setModel(pandasModel(data_df))
        self.input_data = data_df
    
    def slot_show_table_cv(self, data_df):
        self.table_CV.setModel(pandasModel(data_df))
        suggest_columns, suggest_columns_str = [], ''
        if sum(data_df.iloc[:, 1] > 1) > 0: suggest_columns = data_df[data_df[data_df.columns[1]] > 1].iloc[:, 0].values
        elif sum(data_df.iloc[:, 1] > 0.3) > 0: suggest_columns = data_df[data_df[data_df.columns[1]] > 0.3].iloc[:, 0].values
        elif sum(data_df.iloc[:, 1] > 0.15) > 0: suggest_columns = data_df[data_df[data_df.columns[1]] > 0.15].iloc[:, 0].values
        else: suggest_columns = []

        if len(suggest_columns) > 0:
            for i, column in enumerate(suggest_columns):
                if i == 0: suggest_columns_str += '{}({})'.format(column, self.column_eng_chinese_dict[column])
                else: suggest_columns_str += '、{}({})'.format(column, self.column_eng_chinese_dict[column])
        if len(suggest_columns_str) > 0: 
            self.suggest_str += f'● 以下欄位具有較高變異，可能是影響整體資料穩定度的主因：\n\t{suggest_columns_str}\n'
        self.label_suggest.setText(self.suggest_str)

    def slot_message(self, message_str):
        self.label_message.setText(message_str) 
    
    def slot_update_df_message(self, data_df):
        self.table_message.setModel(pandasModel(data_df))
    
    def slot_update_df_errorlog(self, data_df):
        self.data_error_log, suggest_columns_str = data_df, ''
        self.table_error_log.setModel(pandasModel(self.data_error_log))
        if len(data_df) > 0:
            total_error_count = self.data_error_log[self.data_error_log['Index'] == 'Total']
            show_error_boundary = (len(data_df) - 1) / 2
            if max(total_error_count.values[0][2:]) < show_error_boundary: show_error_boundary = max(total_error_count.values[0][2:])
            select_error_columns = total_error_count.iloc[0, [index + 2 for index, i in enumerate(total_error_count.values[0][2:]) if i >= show_error_boundary]].sort_values(ascending = False).index

            if len(select_error_columns) > 0:
                for i, column in enumerate(select_error_columns):
                    if i == 0: suggest_columns_str += '{}({})'.format(column, self.column_eng_chinese_dict[column])
                    else: suggest_columns_str += '、{}({})'.format(column, self.column_eng_chinese_dict[column])
            if len(suggest_columns_str) > 0: 
                self.suggest_str += f'● 以下欄位依序是造成異常模次的主因：\n\t{suggest_columns_str}\n'
            self.label_suggest.setText(self.suggest_str)
        
    def slot_prepare_for_plot(self, data_list):
        data_arg, data_distrance, self.cluster_array = data_list
        DMDA = data_distrance.mean().diff().abs()
        parameter_list = [float(self.edit_DBSCAN1.text()), int(self.edit_DBSCAN2.text()), float(self.edit_sigma_alpha.text()), float(self.edit_sigma_k.text())]

        self.th2_work = WorkThread_plot(self.date, data_arg, data_distrance, DMDA, self.cluster_array, self.plot_output_result, self.plot_cluster, parameter_list)
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