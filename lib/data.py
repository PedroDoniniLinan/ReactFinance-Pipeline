from lib.constants import *
from lib.tools import *

import pandas as pd
import datetime as dt
import numpy as np


# =============== AUX =============== #
def mapAccounts(ticker):
    if ticker in set(['BTC', 'ETH']):
        return BT
    return EASY            


def mapCategory(ticker):
    if ticker in set(['IRDM11']):
        return REAL_STATE
    if ticker in set(['BTC', 'ETH']):
        return CRYPTO
    if ticker in set(['BRAX11', 'BBSD11']):
        return BR_GROWTH
    if ticker in set(['TSLA34']):
        return US_SUPER_GROWTH
    return US_GROWTH    


def getFlexDate(date):
    if date.day >= DATE_TRESHOLD:
        date = date.replace(day=1, month=date.month + 1 if date.month < 12 else 1, year=date.year if date.month < 12 else date.year + 1)
    return date


def computeIncome(row, prices):
    previousMonth = ''
    priceRow = prices[prices[TICKER] == row[TICKER]]
    for c in priceRow.columns:
        if c == TICKER:
            continue
        date = dt.datetime.strptime(c, '%d/%m/%Y')#.date()
        if date < row[DATE]:
            row[c] = 0
        else:
            if previousMonth == '':
                row[c] = (priceRow[c].item() - row[BUY]) * row[SHARES]
            else:
                row[c] = (priceRow[c].item() - priceRow[previousMonth].item()) * row[SHARES]
            previousMonth = c
    return row


def computeFlexibleIncome(row, prices):
    previousMonth = ''
    priceRow = prices[prices[TICKER] == row[TICKER]]
    for c in priceRow.columns:
        if c == TICKER:
            continue
        date = dt.datetime.strptime(c, '%d/%m/%Y')#.date()
        early_begining = date.year == row[DATE].year and date.month == row[DATE].month and row[DATE].day < DATE_TRESHOLD
        late_begining_1 = date.year == row[DATE].year and date.month - 1 == row[DATE].month and row[DATE].day >= DATE_TRESHOLD
        late_begining_2 = date.year - 1 == row[DATE].year and date.month == 1 and row[DATE].month == 12 and row[DATE].day >= DATE_TRESHOLD
        if early_begining or late_begining_1 or late_begining_2:
            row[c] = (priceRow[c].item() - row[BUY]) * row[SHARES]
            previousMonth = c
        elif date < row[DATE]:
            row[c] = 0
        else:
            if previousMonth == '':
                row[c] = 0
            else:
                row[c] = (priceRow[c].item() - priceRow[previousMonth].item()) * row[SHARES]
            previousMonth = c
    return row


def computePositions(row, prices):
    priceRow = prices[prices[TICKER] == row[TICKER]]
    for c in priceRow.columns:
        if c == TICKER:
            continue
        date = dt.datetime.strptime(c, '%d/%m/%Y')#.date()
        if date < row[DATE]:
            row[c] = 0
        else:
            row[c] = priceRow[c].item() * row[SHARES]
    return row    


def computeFlexiblePositions(row, prices):
    priceRow = prices[prices[TICKER] == row[TICKER]]
    for c in priceRow.columns:
        if c == TICKER:
            continue
        date = dt.datetime.strptime(c, '%d/%m/%Y')#.date()
        if date.year == row[DATE].year and date.month == row[DATE].month and row[DATE].day < DATE_TRESHOLD:
            row[c] = priceRow[c].item() * row[SHARES]
        elif (date.year == row[DATE].year and date.month == row[DATE].month and row[DATE].day >= DATE_TRESHOLD) or date <= row[DATE]:
            row[c] = 0
        else:
            row[c] = priceRow[c].item() * row[SHARES]
    return row    


def processPortfolio(portfolio, prices, function, valueColumn):
    months = list(prices.columns)
    months.pop(0)

    tempPortfolio = portfolio.apply(lambda x : function(x, prices), axis=1)
    tempPortfolio = pd.melt(
        tempPortfolio[prices.columns], 
        id_vars=[TICKER], 
        value_vars=months,
        var_name=DATE, 
        value_name=VALUE
    )
    tempPortfolio = tempPortfolio.rename(columns={TICKER: NAME})
    tempPortfolio[CATEGORY] = tempPortfolio[NAME].apply(lambda x: mapCategory(x))
    tempPortfolio[SUBCATEGORY] = tempPortfolio[NAME]
    tempPortfolio = pd.pivot_table(tempPortfolio, values=[VALUE], index=[NAME, CATEGORY, SUBCATEGORY, DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    tempPortfolio = tempPortfolio.rename(columns={VALUE: valueColumn})
    tempPortfolio.set_index([NAME, CATEGORY, SUBCATEGORY, DATE])

    return tempPortfolio


# =============== MAIN =============== #
def computePortfolioIncome(portfolio, filterRemove):
    # portfolio = read('data/data_portfolio_.csv', filterRemove)
    portfolio[DATE] = portfolio[DATE].apply(lambda x : dt.datetime.strptime(str(x),'%d/%m/%Y'))#.date())
    prices = pd.read_csv('data/data_prices.csv')

    portfolio = portfolio.apply(lambda x : computeIncome(x, prices), axis=1)
    months = list(prices.columns)
    months.pop(0)
    cols = prices.columns.tolist()
    cols.insert(1, ACCOUNT)
    portfolioIncome = pd.melt(
        portfolio[cols], 
        id_vars=[TICKER, ACCOUNT], 
        value_vars=months,
        var_name=DATE, 
        value_name=VALUE
    )
    portfolioIncome = portfolioIncome.rename(columns={TICKER: NAME})
    # portfolioIncome[ACCOUNT] = ~portfolioIncome[NAME].apply(lambda x: mapAccounts(x))
    portfolioIncome[CATEGORY] = INVESTMENTS
    portfolioIncome[SUBCATEGORY] = portfolioIncome[NAME]
    # test = pd.pivot_table(portfolioIncome, values=[VALUE], index=[NAME, ACCOUNT, CATEGORY, SUBCATEGORY, DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()

    return portfolioIncome[portfolioIncome[VALUE] != 0]


def readData(filterRemove):
    # income
    income = read('data/data_income.csv', filterRemove)
    portfolioBuy = read('data/data_portfolio_.csv', filterRemove)
    portfolio = computePortfolioIncome(portfolioBuy, filterRemove)
    print(portfolio[portfolio[SUBCATEGORY] == 'BTC'])
    income = pd.concat([income, portfolio])

    income[CATEGORY] = income[CATEGORY].fillna('')
    income[SUBCATEGORY] = income[SUBCATEGORY].fillna('')
    income[DATE] = income[DATE].apply(lambda x : dt.datetime.strptime(str(x),'%d/%m/%Y'))#.date())
    income[DATE] = date_trunc(income[DATE], 'month')
    income = pd.pivot_table(income, values=[VALUE], index=[ACCOUNT, CATEGORY, SUBCATEGORY, DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    income = income.rename(columns={VALUE: INCOME})

    print(income[income[SUBCATEGORY] == 'BTC'])

    # expenses
    expenses = read('data/data_expenses.csv', filterRemove)
    expenses[CATEGORY] = expenses[CATEGORY].fillna('')
    expenses[SUBCATEGORY] = expenses[SUBCATEGORY].fillna('')
    expenses[DATE] = expenses[DATE].apply(lambda x : dt.datetime.strptime(str(x),'%d/%m/%Y'))#.date())
    expenses[DATE] = date_trunc(expenses[DATE], 'month')
    expenses = pd.pivot_table(expenses, values=[VALUE], index=[ACCOUNT, CATEGORY, SUBCATEGORY, DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    expenses = expenses.rename(columns={VALUE: EXPENSES})


    # tranfers
    transfer = read('data/data_transf.csv', filterRemove)
    transfer[DATE] = transfer[DATE].apply(lambda x : dt.datetime.strptime(str(x),'%d/%m/%Y'))#.date())
    transfer[DATE] = date_trunc(transfer[DATE], 'month')
    transferOut = pd.pivot_table(transfer, values=[VALUE], index=[FROM, DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    transferIn = pd.pivot_table(transfer, values=[VALUE], index=[TO, DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()

    transferOut = transferOut.rename(columns={FROM: ACCOUNT})
    transferIn = transferIn.rename(columns={TO: ACCOUNT})

    return income, expenses, transferOut, transferIn


def readNU():
    # income
    income = read('data/data_income.csv', True)
    income[CATEGORY] = income[CATEGORY].fillna('')
    income[SUBCATEGORY] = income[SUBCATEGORY].fillna('')
    income = income[income[ACCOUNT] == NU]
    income[DATE] = income[DATE].apply(lambda x : dt.datetime.strptime(str(x),'%d/%m/%Y'))#.date())

    flexIncome = income.copy()
    flexIncome[DATE] = flexIncome[DATE].apply(lambda x : getFlexDate(x))
    flexIncome[DATE] = date_trunc(flexIncome[DATE], 'month')

    # print(income[income[DATE] < dt.datetime.strptime(str('01/11/2019'),'%d/%m/%Y')])
    income[DATE] = date_trunc(income[DATE], 'month')
    income = pd.pivot_table(income, values=[VALUE], index=[DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    income = income.rename(columns={VALUE: INCOME})

    yieldIncome = flexIncome[flexIncome[SUBCATEGORY] == FIXED_INCOME]
    yieldIncome = pd.pivot_table(yieldIncome, values=[VALUE], index=[DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    yieldIncome = yieldIncome.rename(columns={VALUE: FLEX_INCOME})
    
    flexIncome = pd.pivot_table(flexIncome, values=[VALUE], index=[DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    flexIncome = flexIncome.rename(columns={VALUE: INCOME})

    # expenses
    expenses = read('data/data_expenses.csv', True)
    expenses = expenses[expenses[ACCOUNT] == NU]
    expenses[CATEGORY] = expenses[CATEGORY].fillna('')
    expenses[SUBCATEGORY] = expenses[SUBCATEGORY].fillna('')
    expenses[DATE] = expenses[DATE].apply(lambda x : dt.datetime.strptime(str(x),'%d/%m/%Y'))#.date())
    
    flexExpenses = expenses.copy()
    flexExpenses[DATE] = flexExpenses[DATE].apply(lambda x : getFlexDate(x))
    flexExpenses[DATE] = date_trunc(flexExpenses[DATE], 'month')
    flexExpenses = pd.pivot_table(flexExpenses, values=[VALUE], index=[DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    flexExpenses = flexExpenses.rename(columns={VALUE: EXPENSES})

    expenses[DATE] = date_trunc(expenses[DATE], 'month')
    expenses = pd.pivot_table(expenses, values=[VALUE], index=[DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    expenses = expenses.rename(columns={VALUE: EXPENSES})

    # tranfers
    transfer = read('data/data_transf.csv', True)
    transfer = transfer[(transfer[FROM] == NU) | (transfer[TO] == NU)]
    transfer[DATE] = transfer[DATE].apply(lambda x : dt.datetime.strptime(str(x),'%d/%m/%Y'))#.date())

    flexTransfer = transfer.copy()
    flexTransfer[DATE] = flexTransfer[DATE].apply(lambda x : getFlexDate(x))
    flexTransfer[DATE] = date_trunc(flexTransfer[DATE], 'month')
    flexTransferOut = pd.pivot_table(flexTransfer, values=[VALUE], index=[FROM, DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    flexTransferOut = flexTransferOut[flexTransferOut[FROM] == NU]
    flexTransferIn = pd.pivot_table(flexTransfer, values=[VALUE], index=[TO, DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    flexTransferIn = flexTransferIn[flexTransferIn[TO] == NU]

    flexTransferOut = flexTransferOut.rename(columns={VALUE: 'Out'})
    flexTransferIn = flexTransferIn.rename(columns={VALUE: 'In'})

    transfer[DATE] = date_trunc(transfer[DATE], 'month')
    transferOut = pd.pivot_table(transfer, values=[VALUE], index=[FROM, DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    transferOut = transferOut[transferOut[FROM] == NU]
    transferOut = transferOut[[DATE, VALUE]]
    transferIn = pd.pivot_table(transfer, values=[VALUE], index=[TO, DATE], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    transferIn = transferIn[transferIn[TO] == NU]
    transferIn = transferIn[[DATE, VALUE]]

    transferOut = transferOut.rename(columns={VALUE: 'Out'})
    transferIn = transferIn.rename(columns={VALUE: 'In'})

    # consolidated
    df = income.set_index(DATE).join(expenses.set_index(DATE), rsuffix='_2').join(transferOut.set_index(DATE), rsuffix='_3').join(transferIn.set_index(DATE), rsuffix='_4', how='outer')
    df = df.fillna(0)
    df[POSITION] = df[INCOME] - df[EXPENSES] - df['Out'] + df['In']
    df[POSITION] = df[POSITION].cumsum()
    df = df.reset_index()
    df = df[[DATE, POSITION]]

    flexDf = flexIncome.join(flexExpenses, rsuffix='_2').join(flexTransferOut, rsuffix='_3').join(flexTransferIn, rsuffix='_4')
    flexDf = flexDf.fillna(0)
    flexDf[FLEX_POSITION] = flexDf[INCOME] - flexDf[EXPENSES] - flexDf['Out'] + flexDf['In']
    flexDf[FLEX_POSITION] = flexDf[FLEX_POSITION].cumsum()
    flexDf = flexDf[[DATE, FLEX_POSITION]]

    resultDf = df.join(flexDf, rsuffix='_2').join(yieldIncome, rsuffix='_3')
    resultDf = resultDf[[DATE, POSITION, FLEX_POSITION, FLEX_INCOME]]
    resultDf[CATEGORY] = FIXED_INCOME
    resultDf[SUBCATEGORY] = NU
    return resultDf


def readPortfolio():
    portfolio = read('data/data_portfolio.csv', True)
    portfolio[DATE] = portfolio[DATE].apply(lambda x : dt.datetime.strptime(str(x),'%d/%m/%Y'))#.date())
    prices = pd.read_csv('data/data_prices.csv')

    portfolioFlexibleIncome = processPortfolio(portfolio, prices, computeFlexibleIncome, FLEX_INCOME)
    portfolioFlexPositions = processPortfolio(portfolio, prices, computeFlexiblePositions, FLEX_POSITION)
    portfolioPositions = processPortfolio(portfolio, prices, computePositions, POSITION)

    portfolio = portfolioPositions.join(portfolioFlexibleIncome, rsuffix='_2').join(portfolioFlexPositions, rsuffix='_3')
    portfolio = portfolio[[CATEGORY, SUBCATEGORY, DATE, POSITION, FLEX_POSITION, FLEX_INCOME]]
    portfolio = portfolio[(portfolio[POSITION] != 0) & (portfolio[FLEX_INCOME] != 0) & (portfolio[FLEX_POSITION] != 0)]
    portfolio[DATE] = portfolio[DATE].apply(lambda x : dt.datetime.strptime(str(x),'%d/%m/%Y'))#.date())
    portfolio[DATE] = date_trunc(portfolio[DATE], 'month')

    return portfolio


def validateData(income, expenses, transferOut, transferIn, date):
    filterDate = dt.datetime.strptime(str(date),'%d/%m/%Y')#.date()

    income = income[income[DATE] <= filterDate]
    expenses = expenses[expenses[DATE] <= filterDate]
    transferOut = transferOut[transferOut[DATE] <= filterDate]
    transferIn = transferIn[transferIn[DATE] <= filterDate]

    income = pd.pivot_table(income, values=[INCOME], index=[ACCOUNT], aggfunc={INCOME: np.sum}, fill_value=0)#.reset_index()
    expenses = pd.pivot_table(expenses, values=[EXPENSES], index=[ACCOUNT], aggfunc={EXPENSES: np.sum}, fill_value=0)#.reset_index()
    transferOut = pd.pivot_table(transferOut, values=[VALUE], index=[ACCOUNT], aggfunc={VALUE: np.sum}, fill_value=0)#.reset_index()
    transferIn = pd.pivot_table(transferIn, values=[VALUE], index=[ACCOUNT], aggfunc={VALUE: np.sum}, fill_value=0)#.reset_index()


    transferOut = transferOut.rename(columns={VALUE: 'Out'})
    transferIn = transferIn.rename(columns={VALUE: 'In'})

    df = income.join(expenses).join(transferOut).join(transferIn)
    df = df.fillna(0)
    
    df[VALUE] = df[INCOME] - df[EXPENSES] - df['Out'] + df['In']

    balances = pd.read_csv('data/data_balances.csv')
    balances[DATE] = balances[DATE].apply(lambda x : dt.datetime.strptime(str(x),'%d/%m/%Y'))#.date())
    balances = balances[balances[DATE] == filterDate].set_index(ACCOUNT)
    diff = balances[VALUE] - df[VALUE]
    diff = diff.fillna(0)
    diff = diff.apply(lambda x: round(x, 2))
    if diff.sum() == 0 and balances.size != 0:
        return True
    else:
        print(df)
        print(diff)
        return False


if __name__ == '__main__':
    print('Hi')