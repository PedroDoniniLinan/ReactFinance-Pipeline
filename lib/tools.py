import datetime as dt

def date_trunc(date, unit=None):
    if unit == 'year':
        return date.apply(lambda x : dt.datetime(x.year, 1, 1))#.date())
    else:
        return date.apply(lambda x : dt.datetime(x.year, x.month, 1))#.date())