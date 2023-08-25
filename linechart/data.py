import pandas as pd

d = pd.read_excel('data.xlsx')
# print(d)

times = list(d['HMS'].apply(str))[:120]
# print(type(times[0]))  # <class 'str'>

dealnums = d['笔/秒'][:120]
# print(type(dealnums[0]))  # <class 'numpy.int64'>

vwaps = d['VWAP'][:120]
# print(type(vwaps[0]))  # <class 'numpy.float64'>

