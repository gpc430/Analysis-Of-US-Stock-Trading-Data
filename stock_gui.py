from PyQt5.QtWidgets import *
import matplotlib
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation

from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

matplotlib.use('Qt5Agg')
# plt.style.use('dark_background')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from stock_ui_v1 import Ui_MainWindow
import business_logic
from datetime import datetime
import pandas as pd

specify_now = "2022-05-20 01:05:23"

ani1, ani2, ani3 = None, None, None


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MyMainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.up_down_dict = None
        self.bl = business_logic.Logic(specify_now)
        self._init_widget_values()

    def _init_widget_values(self):
        show_now_time = datetime.strptime(specify_now, "%Y-%m-%d %H:%M:%S")
        self.dateTimeEdit_cur_time.setDateTime(show_now_time)
        # self.dateTimeEdit_cur_time.setReadOnly(True)  # 设置为不可更改
        self.lineEdit_bills_sec.setText(str(self.bl.get_bills_sec()))
        self.lineEdit_turnover_sec.setText(str(self.bl.get_turnover_sec()))
        self.lineEdit_vwap.setText(str(self.bl.get_vwap_sec()))

        self.dateTimeEdit_observe_time.setDateTime(show_now_time)
        N = self.lineEdit_observe_length.text()  # 秒
        self.pushButton_cal_up_down.clicked.connect(lambda: self.cal_up_down(specify_now, N))

        self.draw_pic()

    def cal_up_down(self, T, N):
        self.up_down_dict = self.bl.cal_up_down(T, N)
        self.lineEdit_up_max.setText(str(self.up_down_dict['max_percent']))
        self.lineEdit_down_max.setText(str(self.up_down_dict['min_percent']))
        self.lineEdit_max_price.setText(str(self.up_down_dict['max_price']))
        self.lineEdit_min_price.setText(str(self.up_down_dict['min_price']))
        self.lineEdit_up_down_max.setText(str(self.up_down_dict['min_max_length']))

    def draw_pic(self):
        top_fig = TopFigure(self.bl, width=3, height=2, dpi=100)
        top_fig.plot_vwap()
        self.gridLayout_2.addWidget(top_fig, 0, 0)

        bottom_fig = BottomFigure(self.bl, width=3, height=2, dpi=100)
        bottom_fig.plt_up_sub_down()
        self.gridLayout_2.addWidget(bottom_fig, 1, 0)

        bottom_fig2 = BottomFigure2(self.bl, width=3, height=2, dpi=100)
        bottom_fig2.plt_up_sub_down()
        self.gridLayout_2.addWidget(bottom_fig2, 2, 0)


class TopFigure(FigureCanvas):
    def __init__(self, bl, width=5, height=4, dpi=100):
        self.bl = bl
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(TopFigure, self).__init__(self.fig)  # 此句必不可少，否则不能显示图形
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('0.2')
        self.axes.grid(linewidth=0.4)
        self.init_i = 300
        self.t = None
        self.s, self.s2 = None, None
        self.axes2 = self.axes.twinx()

    def init_figure(self):
        x_data = self.t.iloc[:self.init_i].to_list()
        y1_data = self.s.iloc[:self.init_i].to_list()
        y2_data = self.s2.iloc[:self.init_i].to_list()
        self.axes.plot(x_data, y1_data, c='green', label='VWAP')
        self.axes2.plot(x_data, y2_data, c='purple', label='bill/s')
        self.axes.legend(loc='upper left')
        self.axes2.legend(loc='upper right')

    def update_animation(self, i):
        x_data = self.t.iloc[:i].to_list()
        y1_data = self.s.iloc[: i].to_list()
        y2_data = self.s2.iloc[: i].to_list()
        self.axes.plot(x_data, y1_data, c='green', label='VWAP')
        self.axes2.plot(x_data, y2_data, c='purple', label='bill/s')

    def plot_vwap(self):
        vwap_more_0 = self.bl.p3_result[self.bl.p3_result[business_logic.LR.VWAP] > 0]
        self.t = pd.Series(vwap_more_0.index)
        self.s = vwap_more_0[business_logic.LR.VWAP]
        self.s2 = vwap_more_0[business_logic.LR.BILL]
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.axes2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        global ani1
        ani1 = FuncAnimation(self.fig, self.update_animation, init_func=self.init_figure,
                             frames=range(self.init_i, len(self.t)), interval=1000)


class BottomFigure(FigureCanvas):
    def __init__(self, bl, width=5, height=4, dpi=100):
        self.bl = bl
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(BottomFigure, self).__init__(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(linewidth=0.4)
        self.axes.set_facecolor('0.2')
        self.init_i = 300
        self.BIN_WIDTH = 5
        self.BAR_WIDTH = 0.00005
        self.t, self.s = None, None
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    def init_figure(self):
        s_part = self.s.iloc[:self.init_i]
        s_more_0, s_less_0 = s_part[s_part >= 0], s_part[s_part < 0]
        t0, s0 = s_more_0[::self.BIN_WIDTH].index, s_more_0[::self.BIN_WIDTH]
        t1, s1 = s_less_0[::self.BIN_WIDTH].index, s_less_0[::self.BIN_WIDTH]
        self.axes.bar(t0, s0, width=self.BAR_WIDTH, color='green')
        self.axes.bar(t1, s1, width=self.BAR_WIDTH, color='red')

    def update_animation(self, i):
        s_part = self.s.iloc[:i]
        s_more_0, s_less_0 = s_part[s_part >= 0], s_part[s_part < 0]
        t0, s0 = s_more_0[::self.BIN_WIDTH].index, s_more_0[::self.BIN_WIDTH]
        t1, s1 = s_less_0[::self.BIN_WIDTH].index, s_less_0[::self.BIN_WIDTH]
        self.axes.bar(t0, s0, width=self.BAR_WIDTH, color='green')
        self.axes.bar(t1, s1, width=self.BAR_WIDTH, color='red')

    def plt_up_sub_down(self):
        """
        4. Uptick成交额 - Downtick成交额
        5. 数据4 / 数据2，即：（Uptick成交额 - Downtick成交额）/ 成交额/秒
        :return:
        """
        vwap_more_0 = self.bl.p3_result[self.bl.p3_result[business_logic.LR.VWAP] > 0]
        self.s = (vwap_more_0[business_logic.LR.UPTICK] - vwap_more_0[business_logic.LR.DOWNTICK]) / vwap_more_0[
            business_logic.LR.TURNOVER]
        self.t = self.s.index
        self.axes.set_title("(up-down)/turnover")

        global ani2
        ani2 = FuncAnimation(self.fig, self.update_animation, init_func=self.init_figure,
                             frames=range(self.init_i, len(self.t)), interval=1000)


class BottomFigure2(FigureCanvas):
    def __init__(self, bl, width=5, height=4, dpi=100):
        self.bl = bl
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(BottomFigure2, self).__init__(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(linewidth=0.4)
        self.axes.set_facecolor('0.2')
        self.init_i = 300
        self.BIN_WIDTH = 5
        self.BAR_WIDTH = 0.00005
        self.t, self.s = None, None
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    def init_figure(self):
        s_part = self.s.iloc[:self.init_i]
        s_more_0, s_less_0 = s_part[s_part >= 0], s_part[s_part < 0]
        t0, s0 = s_more_0[::self.BIN_WIDTH].index, s_more_0[::self.BIN_WIDTH]
        t1, s1 = s_less_0[::self.BIN_WIDTH].index, s_less_0[::self.BIN_WIDTH]
        self.axes.bar(t0, s0, width=self.BAR_WIDTH, color='green')
        self.axes.bar(t1, s1, width=self.BAR_WIDTH, color='red')

    def update_animation(self, i):
        s_part = self.s.iloc[:i]
        s_more_0, s_less_0 = s_part[s_part >= 0], s_part[s_part < 0]
        t0, s0 = s_more_0[::self.BIN_WIDTH].index, s_more_0[::self.BIN_WIDTH]
        t1, s1 = s_less_0[::self.BIN_WIDTH].index, s_less_0[::self.BIN_WIDTH]
        self.axes.bar(t0, s0, width=self.BAR_WIDTH, color='green')
        self.axes.bar(t1, s1, width=self.BAR_WIDTH, color='red')

    def plt_up_sub_down(self):
        """
        4. Uptick成交额 - Downtick成交额
        :return:
        """
        vwap_more_0 = self.bl.p3_result[self.bl.p3_result[business_logic.LR.VWAP] > 0]
        self.s = vwap_more_0[business_logic.LR.UPTICK] - vwap_more_0[business_logic.LR.DOWNTICK]
        self.t = self.s.index
        self.axes.set_title("up-down")

        global ani3
        ani3 = FuncAnimation(self.fig, self.update_animation, init_func=self.init_figure,
                             frames=range(self.init_i, len(self.t)), interval=1000)


if __name__ == "__main__":
    app = QApplication([])

    window = MyMainWindow()
    window.setWindowTitle("股票可视化软件")
    window.show()
    app.exec_()
