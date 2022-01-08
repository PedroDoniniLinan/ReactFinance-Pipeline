from lib import data
from lib import tools
from lib import mongo
from lib.constants import *
import pandas as pd
import datetime as dt
import numpy as np

DEBUG = True
DEBUG_CURRENCY = 'FINA'

if __name__ == '__main__':
    # currencies = ['BRL', 'IVVB11', 'AMZO34', 'BBSD11', 'BRAX11', 'DISB34', 'FBOK34', 'GOGL34', 'IRDM11', 'JPMC34', 'MSFT34', 'TSLA34', 'BTC', 'ETH', 'SOL', 'ADA', 'AVAX', 'USDT', 'AXS', 'SLP']
    if DEBUG:
        # currencies = [DEBUG_CURRENCY]
        currencies = ['BRL', DEBUG_CURRENCY]
    else:
        currencies = tools.getActives()
    outputs = {}

    positions = None
    for c in currencies:
        if positions is None: 
            positions = data.readAllocation(c)
        else:
            positions = pd.concat([positions, data.readAllocation(c)])
    print(positions)

    # print('Starting validation...')
    # validated = True
    # for c in currencies:
    #     print(c)
    #     outputs[c] = data.readData(c, truncate=True, filterRemove=False)
    #     v, df = data.validateData(outputs, c, '27/12/2021', True)
    #     validated = validated and v

   
    # if validated:
    #     print('Validation: OK')

    # # print('Calculating removed calculatedBalances...')
    # # realBalance = pd.DataFrame({TICKER : [], VALUE : []})
    # # for c in currencies:
    # #     # print(c)
    # #     outputs[c] = data.readData(c, False)
    # #     temp, df = data.validateData(outputs, c, '04/11/2021', False)
    # #     outputs[c] = data.readData(c, True)
    # #     temp, dfb = data.validateData(outputs, c, '04/11/2021', False)
    # #     active = df.sum()
    # #     if c == 'SLP':
    # #         print(df)
    # #         print(df-dfb)
    # #     realBalance.loc[-1] = [c, active[VALUE]]
    # #     realBalance = realBalance.reset_index(drop=True)

    # print('Calculating balance...')
    # realBalance = pd.DataFrame({TICKER : [], VALUE : []})
    # for c in currencies:
    #     # print(c)
    #     outputs[c] = data.readData(c, truncate=True, filterRemove=True)
    #     temp, df = data.validateData(outputs, c, '27/12/2021', False)
    #     active = df.sum()

    #     realBalance.loc[-1] = [c, active[VALUE]]
    #     realBalance = realBalance.reset_index(drop=True)
    
    # if validated:
    #     currencies = ['BRL']
    #     print('Calculating earnings...')
    #     for c in currencies:
    #         print(c)
    #         exchange = data.readFlow('exchange', None, [], True, None, True)
            
    #         if DEBUG:
    #             exchange = exchange[(exchange[TICKER] == DEBUG_CURRENCY)|(exchange[CURRENCY] == DEBUG_CURRENCY)]
            
    #         exchange[ORIGINAL_CURRENCY] = exchange[CURRENCY]
            
    #         originalExchange = exchange[exchange[CURRENCY] == c].copy()
    #         convertedExchange = exchange[exchange[CURRENCY] != c].copy()

    #         print('- Deport')
    #         deportCompensation = exchange.copy()
    #         deportCompensation[TICKER] = exchange[CURRENCY] 
    #         deportCompensation[CURRENCY] = exchange[TICKER]
    #         deportCompensation[SHARES] = exchange[BUY] * exchange[SHARES]
    #         deportCompensation[ORIGINAL_CURRENCY] = exchange[TICKER]
    #         deportCompensation[TYPE] = deportCompensation[TYPE].apply(lambda x: PURCHASE if x == SALE else SALE)
            
    #         convertedExchange['Test 0'] = convertedExchange.apply(lambda x: x[BUY] * data.getExchange(c, x[ORIGINAL_CURRENCY], x[DATE]), axis=1)
    #         convertedExchangeTemp = convertedExchange.apply(lambda x: data.convertPortfolio(x, c), axis=1)

    #         convertedExchangeTemp['Test'] = convertedExchangeTemp.apply(lambda x: data.getExchange(c, x[TICKER], x[DATE]), axis=1)
    #         convertedExchangeTemp['Diff'] = (convertedExchangeTemp['Test'] - convertedExchangeTemp['Buy']) / convertedExchangeTemp['Buy']
    #         convertedExchangeTemp['Test 2'] = convertedExchangeTemp.apply(lambda x: data.getExchange(c, x[TICKER], tools.getNextMonth(x[DATE])), axis=1)
    #         convertedExchangeTemp['Diff 2'] = (convertedExchangeTemp['Test 2'] - convertedExchangeTemp['Buy']) / convertedExchangeTemp['Buy']
    #         convertedExchangeTemp[BUY] = convertedExchangeTemp.apply(lambda x: x['Test 0'] if x[ORIGINAL_CURRENCY] in ['USDT', 'BUSD', 'USDC', 'USD', 'BRL', 'EUR'] else (x['Test'] if abs(x['Diff']) > 0.3 and abs(x['Diff 2']) > 0.3 or x[TICKER] in ['USDT', 'BUSD', 'USDC', 'USD', 'BRL', 'EUR'] else x[BUY]), axis=1)
    #         convertedExchange = convertedExchangeTemp
        
    #         if DEBUG:
    #             print(convertedExchange[[TICKER, BUY, SHARES, DATE, CURRENCY, ORIGINAL_CURRENCY, 'Test 0', 'Test', 'Diff', 'Test 2', 'Diff 2']])

    #         deportCompensation[CURRENCY] = c
    #         deportCompensation = deportCompensation.join(convertedExchange[[BUY]], rsuffix='Converted').join(exchange[[BUY]], rsuffix='Original')
    #         deportCompensation[BUY] = deportCompensation.apply(lambda x: 1 if pd.isna(x['BuyConverted']) else x['BuyConverted'] / x['BuyOriginal'], axis=1)
    #         exchange = pd.concat([originalExchange, convertedExchange])
    
    #         if DEBUG:
    #             print(deportCompensation)
    #             print(exchange)
            
    #         print('- Aport')
    #         aport = exchange[[TICKER, BUY, SHARES, TYPE, ORIGINAL_CURRENCY]].copy()
    #         aport[VALUE] = aport[BUY] * aport[SHARES]
    #         aport[VALUE] = aport.apply(lambda x: x[VALUE] if x[TYPE] == PURCHASE else -x[VALUE], axis=1)
    #         aportPair = pd.pivot_table(aport, values=[VALUE], index=[TICKER, ORIGINAL_CURRENCY], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    #         aport = pd.pivot_table(aport, values=[VALUE], index=[TICKER], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
            
    #         deport = deportCompensation[[TICKER, BUY, SHARES, TYPE, ORIGINAL_CURRENCY]].copy()
    #         deport[VALUE] = deport[BUY] * deport[SHARES]
    #         deport[VALUE] = deport.apply(lambda x: x[VALUE] if x[TYPE] == PURCHASE else -x[VALUE], axis=1)
    #         deportPair = pd.pivot_table(deport, values=[VALUE], index=[TICKER, ORIGINAL_CURRENCY], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    #         deport = pd.pivot_table(deport, values=[VALUE], index=[TICKER], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()

    #         deportPair = deportPair.rename(columns={TICKER: ORIGINAL_CURRENCY, ORIGINAL_CURRENCY: TICKER})
    #         diff = aportPair.set_index([TICKER, ORIGINAL_CURRENCY]).join(deportPair.set_index([TICKER, ORIGINAL_CURRENCY]), rsuffix='_deport')
    #         diff['Diff'] = diff[VALUE] + diff[VALUE + '_deport']

    #         print('- Gain')
    #         exchange = pd.concat([exchange, deportCompensation])
            
    #         if DEBUG:                
    #             print(exchange)

    #         exchange[SHARES] = exchange.apply(lambda x: x[SHARES] if x[TYPE] == PURCHASE else -x[SHARES], axis=1)
    #         exchangeIncome = data.computePortfolioIncome(exchange, c)
            
    #         if DEBUG:
    #             print(exchangeIncome)

    #         exchangeIncome[CURRENCY] = exchangeIncome[SUBCATEGORY]
    #         gain = pd.pivot_table(exchangeIncome, values=[VALUE], index=[SUBCATEGORY], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    #         gain = gain.rename(columns={SUBCATEGORY: TICKER})
            
    #         calculatedBalance = pd.concat([aport, gain, deport]) 

    #         if DEBUG:
    #             tools.prinT('gain')
    #             print(diff[diff['Diff'] != 0])
    #             print(gain[VALUE].sum())
    #             print(aport[VALUE].sum())
    #             print(deport[VALUE].sum())
    #             print(aport[VALUE].sum() + deport[VALUE].sum())

    #         print('- Income & Expenses')
    #         globalIncome = None
    #         globalExpenses = None
    #         for k in outputs.keys():
    #             tools.prinT(k)
    #             income = data.readFlow('income', k, [CATEGORY, SUBCATEGORY], False, None, True)
    #             expenses = data.readFlow('expenses', k, [CATEGORY, SUBCATEGORY], False, None, True)

    #             income, portIncome = data.calculateBalance(income, c, k, [CATEGORY, SUBCATEGORY, DATE], PURCHASE)
    #             expenses, portExpenses = data.calculateBalance(expenses, c, k, [CATEGORY, SUBCATEGORY, DATE], '')
                
    #             if DEBUG:
    #                 print(income)
    #                 print(portIncome)
    #                 print(portExpenses)
    #                 print(expenses)

    #             income = pd.concat([income, portIncome, portExpenses])

    #             income[CURRENCY] = k
    #             expenses[CURRENCY] = k

    #             totalIncome = income[VALUE].sum() if not income.empty else 0
    #             totalExpenses = expenses[VALUE].sum() if not expenses.empty else 0
    #             calculatedBalance.loc[-1] = [k, totalIncome - totalExpenses]
    #             calculatedBalance = calculatedBalance.reset_index(drop=True)

    #             if globalIncome is None:
    #                 globalIncome = income
    #                 globalExpenses = expenses
    #             else:
    #                 globalIncome = pd.concat([globalIncome, income])
    #                 globalExpenses = pd.concat([globalExpenses, expenses])

    #         calculatedBalance = pd.pivot_table(calculatedBalance, values=[VALUE], index=[TICKER], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()

    #         prices = data.getConvertedPrices(c)
    #         prices[PRICE] = prices.iloc[:,-1:]
    #         prices = prices[[TICKER, PRICE]]

    #         realBalance = realBalance.join(prices.set_index(TICKER), on=TICKER) 
    #         realBalance[TOTAL] = realBalance[VALUE] * realBalance[PRICE]                
    #         realBalance[SHARES] = realBalance[VALUE]               
    #         realBalance = realBalance[[TICKER, SHARES, TOTAL]].join(calculatedBalance.set_index(TICKER), on=TICKER)
    #         realBalance['Diff'] = realBalance[VALUE] - realBalance[TOTAL]
    #         realBalance['Diff'] = realBalance['Diff'].apply(lambda x: round(x, 6))
            
    #         if DEBUG:
    #             tools.prinT('realBalance')
    #             print(realBalance)
    #             print(realBalance[TOTAL].sum())
    #             print(realBalance[VALUE].sum())
            
    #             tools.prinT('caculatedBalance')
    #             print('Income: ' + str(globalIncome[VALUE].sum()))
    #             print('Expenses: ' + str(globalExpenses[VALUE].sum()))
    #             print('Net: ' + str(globalIncome[VALUE].sum() - globalExpenses[VALUE].sum()))
    #             print('Gain: ' + str(exchangeIncome[VALUE].sum()))
    #             print('Total: ' + str(globalIncome[VALUE].sum() - globalExpenses[VALUE].sum() + exchangeIncome[VALUE].sum()))
    #             print(realBalance[VALUE].sum() - (globalIncome[VALUE].sum() - globalExpenses[VALUE].sum() + exchangeIncome[VALUE].sum()))

    #         globalIncome = pd.concat([globalIncome, exchangeIncome])
    #         globalIncome = pd.pivot_table(globalIncome, values=[VALUE], index=[DATE, CATEGORY, SUBCATEGORY], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()
    #         globalExpenses = pd.pivot_table(globalExpenses, values=[VALUE], index=[DATE, CATEGORY, SUBCATEGORY], aggfunc={VALUE: np.sum}, fill_value=0).reset_index()

    #         globalIncome = globalIncome[globalIncome[VALUE] != 0]
    #         globalExpenses = globalExpenses[globalExpenses[VALUE] != 0]
            
    #         if DEBUG:
    #             print(globalIncome[VALUE].sum())
    #             print(globalExpenses[VALUE].sum())
    #             print(globalIncome[VALUE].sum() - globalExpenses[VALUE].sum())
            
    #         calculationError = round(realBalance[VALUE].sum() - (globalIncome[VALUE].sum() - globalExpenses[VALUE].sum()), 6)
    #         print('Calculation Error: ' + str(calculationError))

    #         globalIncome = globalIncome.rename(columns={VALUE: INCOME})
    #         globalExpenses = globalExpenses.rename(columns={VALUE: EXPENSES})

    #         if DEBUG:
    #             print(globalIncome[globalIncome[SUBCATEGORY] == DEBUG_CURRENCY])
    #             print(globalExpenses[globalExpenses[SUBCATEGORY] == 'Defina'])

    #         if calculationError == 0 and not DEBUG:
    #             print('Calculation: OK')
    #             records = globalIncome.to_dict('records') + globalExpenses.to_dict('records')
    #             # positionsRecords = positions.to_dict('records')
    #             print('Uploading data...')
    #             mongo.replaceInsert(records, 'test')
    #             # mongo.replaceInsert(positionsRecords, 'positions')
    #             print('DONE')

    # # # nuPosition = data.readNU()
    # # # portfolioPositions = data.readPortfolio()
    # # # positions = pd.concat([nuPosition, portfolioPositions])

    # # # print('Validating...')
    # # # if data.validateData(income, expenses, transferOut, transferIn, '04/11/2021'):
    # # #     income, expenses, transferOut, transferIn = data.readData(True)
    # # #     print('Validation: OK')
    # # #     records = income.to_dict('records') + expenses.to_dict('records')
    # # #     # positionsRecords = positions.to_dict('records')
    # # #     print('Uploading data...')
    # # #     # mongo.replaceInsert(records, 'test')
    # # #     # mongo.replaceInsert(positionsRecords, 'positions')
    # # #     print('DONE')
