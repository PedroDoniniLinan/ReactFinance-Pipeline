from lib import data
from lib import tools
from lib import mongo
from lib.constants import *
import pandas as pd
import datetime as dt
import numpy as np

DEBUG = False

if __name__ == '__main__':
    lines = []
    with open('distribution.txt') as f:
        lines = f.readlines()

    df = pd.DataFrame([], columns=['Date', 'Ticker', 'Value', 'Wallet', 'Type', 'Interest type'])
    row = []
    count = 0
    for line in lines:
        count += 1
        # print(f'line {count}: {line}')
        if count == 3:
            row.append(float(line.strip()))
        elif count == 1:
            date = dt.datetime.strptime(line[0:10].strip(), '%Y-%m-%d').date()
            row.append(date) 
        else:
            row.append(line.strip()) 
        if count == 6:
            count = 0
            df.loc[-1] = row # adding a row
            df = df.reset_index(drop=True)  # shifting index
            row = []
    print(df)
    df[DATE] = tools.date_trunc(df[DATE], 'month')
    interest = pd.pivot_table(df, values=[VALUE], index=[DATE, TICKER], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    interest[NAME] = 'Staking'
    interest[ACCOUNT] = 'BNB'
    interest[DATE] = interest[DATE].apply(lambda x: x.strftime('%d/%m/%Y'))
    interest[CATEGORY] = 'Investment'
    interest[SUBCATEGORY] = interest[TICKER]
    interest['Remove'] = 'False'
    interest[CURRENCY] = interest[TICKER]
    interest = interest[[NAME, VALUE, DATE, ACCOUNT, CATEGORY, SUBCATEGORY, 'Remove', CURRENCY]]
    print(interest)
    interest.to_csv('insterest.csv', index=False)
