from lib.constants import *

import datetime as dt
import pandas as pd

def date_trunc(date, unit=None):
    if unit == 'year':
        return date.apply(lambda x : dt.datetime(x.year, 1, 1))#.date())
    else:
        return date.apply(lambda x : dt.datetime(x.year, x.month, 1))#.date())

def read(path, filterRemove):
    df = pd.read_csv(path)
    if filterRemove:
        df = df[df[REMOVE] == False]
    df.pop(REMOVE)
    return df
