from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

import linechart.data as data


def draw_lines(f, x, y1, y2):
    """
    绘制双折线图，双Y轴
    :param f: pyplot figure对象
    :param x: x轴数据
    :param y1: 第一根折线Y轴数据
    :param y2: 第二根折线Y轴数据
    :return:
    """
    ax1 = f.add_subplot(1, 1, 1)
    ax1.plot(x, y1, c='g', label='成交量')
    ax1.grid()
    ax1.set_ylabel('笔/秒')
    ax1.legend(loc='upper left')

    ax1.set_facecolor('0.2')

    ax1.set_xlim(x[0], x[-1])
    ax1.set_xticks(range(0, len(x), 5))

    ax2 = ax1.twinx()
    ax2.plot(x, y2, c='r', label='VWAP')
    ax2.legend(loc='upper right')

    return ax1


start_index = 0
end_index = 5000
max_show_points = 3000000

xdata = []
y1data = []
y2data = []

# plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一(替换sans-serif字体)
# plt.rcParams['axes.unicode_minus'] = False  # 步骤二(解决坐标轴负数的负号显示问题)

fig = plt.figure(figsize=(16, 9), dpi=80)


def init_figure():
    global xdata, y1data, y2data
    xdata = data.times[:end_index]
    y1data = data.dealnums[:end_index]
    y2data = data.vwaps[:end_index]

    ln = draw_lines(fig, xdata, y1data, y2data)

    return ln


def update(i):
    global xdata, y1data, y2data, start_index, end_index
    if len(xdata) < max_show_points:
        end_index += 1
    else:
        start_index += 1
        end_index += 1

    xdata = data.times[start_index:end_index]
    y1data = data.dealnums[start_index:end_index]
    y2data = data.vwaps[start_index: end_index]

    plt.clf()
    return draw_lines(fig, xdata, y1data, y2data)


ani = FuncAnimation(fig, update, init_func=init_figure, interval=1000)

plt.show()
