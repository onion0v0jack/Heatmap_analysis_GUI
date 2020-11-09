import datetime
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.font_manager import FontProperties
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from scipy.spatial import distance_matrix

# warnings.filterwarnings("ignore") # 要求忽略warning
import matplotlib.pyplot as plt
plt.style.use('ggplot')   # 設定畫圖風格為ggplot
plt.rcParams['font.sans-serif'] = ['SimHei'] # 設定相容中文 
plt.rcParams['axes.unicode_minus'] = False
pd.options.mode.chained_assignment = None

class WorkThread(QThread):
    signal_data_table = Signal(pd.DataFrame)
    signal_action = Signal(str)
    signal_data_list_for_plot = Signal(list)

    def __init__(self, date, filename):
        super().__init__()

        self.date = date
        self.filename = filename
        self.input_data = None
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
        self.output_data = pd.DataFrame()


    def run(self):
        try:
            self.signal_action.emit(f'載入資料中...')
            self.input_data = pd.read_table(r'{}'.format(self.filename), sep = ',')
            self.input_data['TriggerTime'] = pd.to_datetime(self.input_data['TriggerTime'])
            self.input_data['CreateTime'] = pd.to_datetime(self.input_data['CreateTime'])
            print(self.input_data.head(3))
            self.input_data = self.input_data[self.input_data['TriggerTime'].dt.strftime('%Y-%m-%d') == self.date]
        except:
            self.signal_action.emit(f'無法載入資料，請檢查資料內容是否有誤')
        else:
            self.signal_action.emit(f'資料轉換中...')
            if len(self.input_data) > 0:
                self.input_data.reset_index(drop = True, inplace = True)
                new_log33 = []
                for i in range(self.input_data.shape[0]):
                    line_data, raw_data = [], self.input_data.loc[i, :].values
                    line_data.extend(raw_data[[0, 2, 3, 1]]) #seq, eq_ip, catch_sn, wNumofshot
                    monitor_data = raw_data[4].split(',')
                    monitor_select_list = [float(monitor_data[i]) for i in self.column_index_eng_dict.keys()] #43 log33 monitor variables
                    line_data += monitor_select_list
                    new_log33.append(line_data)
                self.output_data = pd.DataFrame(new_log33, columns = ['seq', 'eq_ip', 'catch_sn', 'wNumofshot'] + [i for i in self.column_index_eng_dict.values()])
                self.output_data = self.output_data.sort_values('seq')
                self.output_data['catch_sn'] = pd.to_datetime(self.output_data['catch_sn'])
                self.output_data['seq'] = self.output_data.index
                self.signal_action.emit(f'資料轉換完成')
                print(self.output_data.head(3))
                self.signal_data_table.emit(self.output_data)

                self.input_data = None
                data_window_arg = self.output_data.iloc[:, :4]
                data_window_ori = self.output_data.iloc[:, 4:]
                data_window_arg.reset_index(drop = True, inplace = True)
                data_window_ori.reset_index(drop = True, inplace = True)
                self.output_data = None    
                Distance_matrix = pd.DataFrame(distance_matrix(data_window_ori.values, data_window_ori.values), index = data_window_ori.index, columns = data_window_ori.index)
                print(Distance_matrix.shape)
                self.signal_data_list_for_plot.emit([data_window_arg, Distance_matrix])
            else:
                self.signal_action.emit(f'此日期無資料')

class WorkThread_plot(QThread):
    signal_plot = Signal(object)

    def __init__(self, date, arg, distance, criteria, plot_widget):
        super().__init__()

        self.date = date
        self.data_arg = arg
        self.data_distrance = distance
        self.DMDA = criteria
        self.plot = plot_widget


    def run(self):
        self.plot.setRows()
        g1 = sns.heatmap(
            self.data_distrance, linewidths = 0, cmap = 'Reds', square = True, 
            vmin = 0, vmax = 100, cbar_kws = {"shrink": .6},
            ax = self.plot.canvas.ax[0]
        )
        title = '{} 資料的距離熱圖'.format(self.date)
        self.plot.canvas.ax[0].set_title(title, fontproperties = FontProperties(fname = "SimHei.ttf", size = 14), pad = 30)
        self.plot.canvas.ax[0].set_xticklabels(g1.get_xticklabels(), rotation = 90)
        self.plot.canvas.ax[0].set_yticklabels(g1.get_yticklabels(), rotation = 0)
        self.plot.canvas.ax[0].xaxis.tick_top() # x axis on top
        self.plot.canvas.ax[0].xaxis.set_label_position('top')
        self.plot.canvas.ax[0].set_ylabel('Index', fontproperties = FontProperties(fname = "SimHei.ttf", size = 14), rotation = 90)
        self.plot.canvas.ax[0].xaxis.set_tick_params(labelsize = 6)
        self.plot.canvas.ax[0].yaxis.set_tick_params(labelsize = 6)

        self.plot.canvas.ax[1].plot(
            self.data_arg.index, self.data_arg.loc[:, 'catch_sn'], 
            '--o', markersize = 3, linewidth = 1, 
            color = 'k', markerfacecolor = 'steelblue', markeredgecolor = 'steelblue'
        )    
        self.plot.canvas.ax[1].set_xlabel('Index', fontproperties = FontProperties(fname = "SimHei.ttf", size = 14))
        self.plot.canvas.ax[1].set_xlim(-len(self.data_arg)*0.05, len(self.data_arg)*1.05)
        self.plot.canvas.ax[1].set_title(r'索引對應時間記錄與前後差異指數$\sigma_{i}$', fontproperties = FontProperties(fname = "SimHei.ttf", size = 14))
        self.plot.canvas.ax[1].xaxis.set_tick_params(labelsize = 8)
        self.plot.canvas.ax[1].yaxis.set_tick_params(labelsize = 8)
        
        
        ax2_twin = self.plot.canvas.ax[1].twinx()
        ax2_twin.plot(
            self.DMDA.index, self.DMDA, 
            '-o', markersize = 3, linewidth = 1,
            color = 'lightcoral', markerfacecolor = 'tomato', markeredgecolor = 'tomato'
        )
        ax2_twin.set_ylabel(r'$\sigma_{i}$', fontproperties = FontProperties(fname = "SimHei.ttf", size = 14), rotation = 0, labelpad = 25)
        ax2_twin.yaxis.set_tick_params(labelsize = 8)
        if self.DMDA.max() > 10:
            ax2_twin.set_ylim(-1, self.DMDA.max()*1.025)
        else:
            ax2_twin.set_ylim(-1, 10)

        self.plot.canvas.figure.tight_layout()
        self.plot.canvas.draw()
        self.signal_plot.emit(self.plot)