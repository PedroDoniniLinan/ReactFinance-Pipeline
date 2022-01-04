from lib.constants import *

import datetime as dt
import pandas as pd


def date_trunc(date, unit=None):
    if unit == 'year':
        return date.apply(lambda x : dt.datetime(x.year, 1, 1))#.date())
    else:
        return date.apply(lambda x : dt.datetime(x.year, x.month, 1))#.date())


def getNextMonth(date, unit=None):
    if date.month == 12:
        return dt.datetime(date.year + 1, 1, 1)
    else:
        return dt.datetime(date.year, date.month + 1, 1)


def getPrevMonth(date, unit=None):
    if date.month == 1:
        return dt.datetime(date.year - 1, 12, 1)
    else:
        return dt.datetime(date.year, date.month - 1, 1)


def read(path, currency, filterRemove):
    df = pd.read_csv(path)
    if not(currency is None):
        df = df[df[CURRENCY] == currency]
    if filterRemove:
        df = df[df[REMOVE] == False]
    df.pop(REMOVE)
    return df


def getActives():
    df = pd.read_csv('data/data_exchange.csv')
    return sorted(list(set(list(df[TICKER].unique())) | set(list(df[CURRENCY].unique()))))


def prinT(text):
    print('--------------- ' + text + ' ---------------')