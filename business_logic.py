import pandas as pd
from stock_local_analysis import *

LOCAL_FILENAME = "0519.xlsx"


class LR:
    HMS = "HMS"
    BILL = "笔/秒"
    TURNOVER = "成交额/秒"
    UPTICK = "uptick成交额"
    DOWNTICK = "downtick成交额"
    VWAP = "VWAP"


class Logic:
    def __init__(self, specify_now):
        self.specify_now = specify_now
        self.lc = None
        self.observe_dict = None
        self.p3_result = None
        self._read_local_data()

    def _read_local_data(self):
        self.lc = LocalCalcu(LOCAL_FILENAME)
        self.lc.run()
        self.observe_dict = self.lc.observe_dict
        self.p3_result = self.observe_dict['bill_table']

    def get_bills_sec(self):
        """每秒多少笔"""

        return self.p3_result.loc[self.p3_result.index == self.specify_now, LR.BILL].iloc[0]

    def get_turnover_sec(self):
        """每秒多少成交额"""
        return self.p3_result.loc[self.p3_result.index == self.specify_now, LR.TURNOVER].iloc[0]

    def get_vwap_sec(self):
        """每秒多少turnover"""
        return self.p3_result.loc[self.p3_result.index == self.specify_now, LR.VWAP].iloc[0]

    def cal_up_down(self, T, N):
        self.lc.cal_observe(T, N)
        return self.observe_dict
