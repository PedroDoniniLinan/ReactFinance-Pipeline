from lib import data
from lib import mongo
from lib.constants import *
import pandas as pd


if __name__ == '__main__':
    print('Starting pipeline...')
    income, expenses, transferOut, transferIn = data.readData(False)
    nuPosition = data.readNU()
    portfolioPositions = data.readPortfolio()
    positions = pd.concat([nuPosition, portfolioPositions])

    print('Validating...')
    if data.validateData(income, expenses, transferOut, transferIn, '05/09/2021'):
        income, expenses, transferOut, transferIn = data.readData(True)
        print('Validation: OK')
        records = income.to_dict('records') + expenses.to_dict('records')
        positionsRecords = positions.to_dict('records')
        print('Uploading data...')
        mongo.replaceInsert(records, 'test')
        mongo.replaceInsert(positionsRecords, 'positions')
        print('DONE')
