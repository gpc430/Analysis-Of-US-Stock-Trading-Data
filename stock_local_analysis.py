"""
用户提供：
某个时间点T（下称T时刻），观察期N秒

脚本输出：
1、按秒计算的流速(笔/秒)，占一行；按秒计算的流量（成交额/秒）。该秒内如无成交数据，也要生成带有该秒时间的行，数据值为0，不要跳秒，便于绘图。
2、该秒内的 累计uptick成交额 & 累计downtick成交额 （turnover)，如该行的tick为DOWN，该笔turnover计入累计downtick；如该行的tick为UP，该笔turnover计入累计uptick
3、该秒内的VWAP：该秒内的 累计成交额/累计成交量
4、找到T时刻前一笔的价格（下称P），用这个价格计算出T时刻后上涨或下跌0.5%、1%、1.5%、2%的时间点
5、股价在T时点开始后，观察期N结束前，期间上涨和下跌的最大比例%，例如T时点9：45：00，N为120秒，则观察9：45：00 - 9：46：59之间所有成交，相对于T时刻前最后一笔的价格P，涨跌幅度为多少。

注意事项：
1. Python3.6及以上，安装pandas版本1.3.4
2. 输入的excel表格从第6行开始是表头，第7行开始是数据域
3. excel中Timestamp的格式要求为：14-May-2022 07:59:52.977
4. 执行脚本路径与excel位于统一路径下
"""
import time
import pandas as pd


# T = "2022-05-14 00:43:28"
# N = 60  # 秒

# T = input("请输入某个时间点T，格式为yyyy-mm-dd HH:MM:SS:\n")  # 2022-05-14 00:43:28
# N = float(input("请输入观察期N秒，必须为数值型且必须不小于2秒:\n"))  # 60
# filename = input("请输入excel文件名称，要求与脚本位于同一路径下:\n")  # 测试数据.xlsx


class DC:
    Timestamp = "Timestamp"
    Tick = "Tick"
    Volume = "Volume"
    Turnover = "Turnover"
    HMS = "HMS"
    Price = "Last Trade"


class LocalCalcu:
    def __init__(self, filename):
        self.T = None
        self.N = None
        self.filename = filename
        self.df_source = None
        self.observe_dict = {}

    def run(self):
        print(f'开始读入数据，当前时刻: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
        self.df_source: pd.DataFrame = pd.read_excel(self.filename, header=5)
        print(f'完成数据读入，当前时刻: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')

        self.df_source[DC.Timestamp] = pd.to_datetime(self.df_source[DC.Timestamp])
        self.df_source.sort_values(by=[DC.Timestamp], inplace=True)
        self.df_source.reset_index(inplace=True, drop=True)
        self.df_source[DC.HMS] = pd.to_datetime(self.df_source[DC.Timestamp].dt.strftime("%Y-%m-%d %H:%M:%S"))

        result1 = self.df_source.pivot_table(values=[DC.Turnover, DC.Volume], columns=[DC.Tick], index=[DC.HMS],
                                             aggfunc=['count', 'sum'])
        result1.fillna(0, inplace=True)
        final_result1 = pd.DataFrame(columns=['笔/秒', '成交额/秒', 'uptick成交额', 'downtick成交额', 'VWAP'])
        final_result1['笔/秒'] = result1[result1.columns[0]] + result1[result1.columns[1]]
        final_result1['成交额/秒'] = result1[result1.columns[4]] + result1[result1.columns[5]]
        final_result1['uptick成交额'] = result1[result1.columns[5]]
        final_result1['downtick成交额'] = result1[result1.columns[4]]
        final_result1['VWAP'] = final_result1['成交额/秒'] / (result1[result1.columns[-1]] + result1[result1.columns[-2]])
        # 该秒内如无成交数据，也要生成带有该秒时间的行，数据值为0
        beg_s, end_s = self.df_source[DC.HMS].min(), self.df_source[DC.HMS].max()  # 统计开始时刻-结束时刻
        range_s = pd.date_range(beg_s, end_s, freq='S', name=DC.HMS)
        final_result1 = final_result1.reindex(range_s)
        final_result1.fillna(0, inplace=True)
        final_result1.to_excel('前三个问题的汇总结果.xlsx', index=True)
        print('成功，前三个问题的汇总结果.xlsx保存在当前目录下')
        self.observe_dict.update({"bill_table": final_result1})

    def cal_observe(self, T, N):
        self.T = T
        self.N = float(N)
        # 找到T时刻前一笔的价格（下称P），用这个价格计算出T时刻后上涨或下跌0.5%、1%、1.5%、2%的时间点
        pre_stock = self.df_source[self.df_source[DC.Timestamp] < pd.Timestamp(self.T)]
        if len(pre_stock) > 0 or self.df_source.iloc[pre_stock.index[-1]:] > 0:
            P_row = pre_stock.iloc[-1]
            P = P_row[DC.Price]
            print(f"T时点前最后一笔成交的价格P：{P}")
            tmp = self.df_source.iloc[pre_stock.index[-1]:]
            abs_deltas = (0.005, 0.01, 0.015, 0.02)
            final_result2 = []
            for abs_delta in abs_deltas:
                s1 = tmp[(round((P - tmp[DC.Price]) / P, 4) - abs_delta > 0) & (
                        (round((P - tmp[DC.Price]) / P, 4) - abs_delta) < 9.99e-4)]
                if len(s1) > 0:
                    final_result2.append((str(s1.iloc[0][DC.Timestamp]), f'下跌{abs_delta:.1%}'))

                s2 = tmp[(round((tmp[DC.Price] - P) / P, 4) - abs_delta > 0) & (
                        (round((tmp[DC.Price] - P) / P, 4) - abs_delta) < 9.99e-4)]
                if len(s2) > 0:
                    final_result2.append((str(s2.iloc[0][DC.Timestamp]), f'上涨{abs_delta:.1%}'))
            print(final_result2)

            # 股价在T时点开始后，观察期N结束前，期间上涨和下跌的最大比例%
            observe1, observe2 = pd.Timestamp(self.T), pd.Timestamp(self.T) + pd.Timedelta(seconds=self.N - 1)
            tmp2 = self.df_source[
                (observe1 < self.df_source[DC.Timestamp]) & (self.df_source[DC.Timestamp] <= observe2)]
            price_deltas = (tmp2[DC.Price] - P) / P
            max_decrease, max_increase = min(price_deltas), max(price_deltas)
            self.observe_dict.update({"max_price": max(tmp2[DC.Price]), "max_percent": f"{max_increase:.2%}",
                                      "min_price": min(tmp2[DC.Price]), "min_percent": f"{max_decrease:.2%}",
                                      "min_max_length": f"{(max_increase - max_decrease):.2%}"})

            print(f"观察期内最高价为{max(tmp2[DC.Price])}, 最大涨幅: {max_increase:.2%}")
            print(f"观察期内最低价为{min(tmp2[DC.Price])}, 最大跌幅: {max_decrease:.2%}")
            pd.DataFrame({"最大跌幅": [f"{max_decrease:.2%}"], "最大涨幅": [f"{max_increase:.2%}"],
                          "涨跌幅最大区间": [f"{(max_increase - max_decrease):.2%}"]},
                         index=[f"{observe1}-{observe2}"]).to_excel(
                "问题五答案.xlsx")

        else:
            print("T时刻前一笔不存在")

        pd.DataFrame(final_result2).to_excel("问题四答案.xlsx")

        print(f'全部计算完成，当前时刻: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}，程序结束')
