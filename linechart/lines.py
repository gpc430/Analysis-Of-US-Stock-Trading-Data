from matplotlib import pyplot as plt

import data


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
    ax1.plot(x, y1, c='g', label='turnover')
    ax1.grid()
    ax1.set_ylabel('b/s')
    ax1.legend(loc='upper left')

    ax1.set_facecolor('0.2')

    ax1.set_xlim(x[0], x[-1])
    ax1.set_xticks(range(0, len(x), 5))

    ax2 = ax1.twinx()
    ax2.plot(x, y2, c='r', label='VWAP')
    ax2.legend(loc='upper right')


def create_chart(max_show_points: int = 30, pause_time: float = 1):
    """
    绘制动态折线图
    :param max_show_points: 最多显示的数据点，默认30个点
    :param pause_time: 绘制周期，默认1秒
    :return:
    """
    # 显示中文设置
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一(替换sans-serif字体)
    # plt.rcParams['axes.unicode_minus'] = False  # 步骤二(解决坐标轴负数的负号显示问题)

    plt.ion()  # 启用交互模式
    fig = plt.figure(figsize=(16, 9), dpi=80)

    datetimes = []  # 日期时间轴
    deals = []  # 每秒成交量
    vwap_list = []  # vwap数据集

    max_points = max_show_points

    # 动态加载数据并绘图
    for dt, d, v in zip(data.times, data.dealnums, data.vwaps):
        # 清空画布，重新绘图
        plt.clf()

        datetimes.append(dt)
        deals.append(d)
        vwap_list.append(v)

        # 截取指定数量的数据点
        if len(datetimes) > max_points:
            datetimes = datetimes[-max_points:]
            deals = deals[-max_points:]
            vwap_list = vwap_list[-max_points:]

        # 绘制双折线
        draw_lines(fig, datetimes, deals, vwap_list)

        fig.autofmt_xdate()
        plt.pause(pause_time)

    plt.ioff()  # 关闭交互模式
    plt.show()  # 展示最后一张图


if __name__ == '__main__':
    create_chart(60, 0.2)
