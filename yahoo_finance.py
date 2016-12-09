# Author: Prashant (_P0W!)
# Extracts Stocks data from yahoo finance to analyze bullish percentage for given EMA period

from urllib.request import *
from urllib.parse import *
import datetime
import csv

from dateutil.relativedelta import relativedelta

                 
base_url =r'http://chart.finance.yahoo.com/table.csv?s=%(symbol)s%(fromDate)s%(toDate)s&g=d&ignore=.csv'

def getDate( d ):
    x = [ int(s) for s in d.strftime('%m %d %Y').split() ]
    return { 'month':x[0]-1, 'day':x[1],'year':x[2] }

def SMA( data, startRow = 0, period = 200,  ):
    return sum( float(x['Close']) for x in data[startRow:(period)] )/period

def BullishScore( data,period = 200 ):
    return '%.2f' % ( 100.0 * sum( x['AboveEMA'] for x in data[period-1: len(data) ] )/( len(data) - period  ) )
    
def EMA( data,  startRow = 0, period = 200 ):
    index = period - 1
    if startRow == 0:
        data[ index + startRow  ]['EMA'] =  SMA( data, 0, period )
    else:
        factor = 2.0 / ( period + 1 )
        data[ index + startRow]['EMA'] = ( float(data[ index + startRow ]['Close']) -  data[ index + startRow -1]['EMA'] ) * factor + data[ index + startRow -1 ]['EMA']
        data[ index + startRow]['AboveEMA'] =   float(data[ index + startRow ]['Close']) > data[ index + startRow]['EMA'] 


def pull_historical_data( ticker_symbol, period = 200 ):
    fromDate= ( "&a=%(month)d&b=%(day)d&c=%(year)d" % getDate ( datetime.date.today() - relativedelta(years=5)) )
    toDate=   ( "&d=%(month)d&e=%(day)d&f=%(year)d" % getDate ( datetime.date.today() ) )
    csvFileName = r"C:/temp"  + "/" + ticker_symbol + ".csv"
    x = { 'symbol':ticker_symbol, 'fromDate':fromDate, 'toDate':toDate , 'csvFileName' :csvFileName }
    try:
        urlretrieve( base_url % x , x['csvFileName'] )
    except ContentTooShortError as e:
        print ( str(e) )
        pass


    with open( x['csvFileName'],'r') as fin: 
        dr = csv.DictReader(fin) 
        to_db = [ { 'Date':i['Date'], 'Close': i['Adj Close'], 'EMA':0.0, 'AboveEMA':0 } for i in dr]

        
    to_db = sorted( to_db, key=lambda k: k['Date'])

    for row in range(0, len(to_db) - period + 1   ):
        EMA( to_db, row, period )
    
    return to_db



#stocks = [ 'SBIN', 'MARUTI', 'EICHERMOT', 'BERGEPAINT', 'TCS', 'DABUR', 'KAJARIACER'  , 'AJANTPHARM', 'INFY' ]
stocks = [
'SBIN',
'BANKBARODA',
'TATAPOWER',
'ACC',
'ICICIBANK',
'ZEEL',
'HINDALCO',
'TECHM',
'AXISBANK',
'INDUSINDBK',
'ONGC',
'ITC',
'HCLTECH',
'RELIANCE',
'NTPC',
'TATAMOTORS',
'AMBUJACEM',
'ASIANPAINT',
'BHEL',
'AUROPHARMA',
'YESBANK',
'INFY',
'HINDUNILVR',
'IDEA',
'MARUTI',
'HDFCBANK',
'TATAMTRDVR',
'TCS',
'BHARTIARTL',
'TATASTEEL',
'LT',
'WIPRO',
'GAIL',
'ULTRACEMCO',
'SUNPHARMA',
'ADANIPORTS',
'POWERGRID',
'BPCL',
'KOTAKBANK',
'BOSCHLTD',
'LUPIN',
'DRREDDY',
'CIPLA',
'HEROMOTOCO',
'HDFC',
'COALINDIA',
'M&M',
'EICHERMOT',
'GRASIM',

'INFRATEL',
#'BAJAJ-AUTO',
]

for s in stocks:
    data = pull_historical_data('%s.BO' % s, 20 )
    print ( '%-20s is %s %% Bullish with Increase rate of %.2f' % ( s, BullishScore( data ), ( float(data[-1]['Close']) - float(data[0]['Close']))/1305 ) )
    

