# Author: Prashant (_P0W!)
# Extracts Stocks data from yahoo finance to analyze bullish percentage for given EMA period


from urllib.request import *
from urllib.parse import *
import datetime
import csv
import math

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

def fixSplitShare( data ):
    splitRatio = 1.0
    for i in range(len(data[1:])):
        data[i]['Close'] = float(data[i]['Close']) / splitRatio
        if float(data[i-1]['Close']) !=0:
            ratio = float(data[i]['Close'])/float(data[i-1]['Close'])
            if  ratio > 1.45:
                if int(math.ceil(ratio) ) % 2 != 0:
                    finalRatio = math.floor(ratio)
                else:
                    finalRatio = math.ceil(ratio)
                splitRatio = splitRatio * finalRatio
                #print ('CAUTION Got Split Share on %s of %.2f\n' %  ( data[i]['Date'], finalRatio ) )
        

def pull_historical_data( ticker_symbol, period = 200, timeDuration = 5 ):
    fromDate= ( "&a=%(month)d&b=%(day)d&c=%(year)d" % getDate ( datetime.date.today() - relativedelta(years=timeDuration)) )
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
        to_db = [ { 'Date':i['Date'], 'Close': i['Adj Close'], 'EMA':0.0, 'Ratio':0.0, 'AboveEMA':0 } for i in dr]

    fixSplitShare( to_db )
    to_db = sorted( to_db, key=lambda k: k['Date'])
    
                   
    for row in range(0, len(to_db) - period + 1   ):
        EMA( to_db, row, period )
    
    return to_db



#stocks = [ 'SBIN', 'MARUTI', 'EICHERMOT', 'BERGEPAINT', 'TCS', 'DABUR', 'KAJARIACER'  , 'AJANTPHARM', 'INFY' ]
stocks = [
'ACC',
'ADANIPORTS',
'AMBUJACEM',
'ASIANPAINT',
'AUROPHARMA',
'AXISBANK',
#'BAJAJ-AUTO',
'BANKBARODA',
'BHARTIARTL',
'BHEL',
'BOSCHLTD',
'BPCL',
'CIPLA',
'COALINDIA',
'DRREDDY',
'EICHERMOT',
'GAIL',
'GRASIM',
'HCLTECH',
'HDFC',
'HDFCBANK',
'HEROMOTOCO',
'HINDALCO',
'HINDUNILVR',
'ICICIBANK',
'IDEA',
'INDUSINDBK',
'INFRATEL',
'INFY',
'ITC',
'KOTAKBANK',
'LT',
'LUPIN',
'M&M',
'MARUTI',
'NTPC',
'ONGC',
'POWERGRID',
'RELIANCE',
'SBIN',
'SUNPHARMA',
'TATAMOTORS',
'TATAMTRDVR',
'TATAPOWER',
'TATASTEEL',
'TCS',
'TECHM',
'ULTRACEMCO',
'WIPRO',
'YESBANK',
'ZEEL',
]

for s in stocks:
    data = pull_historical_data('%s.BO' % s, 200, 3 )
    print ( '%-20s is %s %% Bullish with Increase rate of %.2f' % ( s, BullishScore( data ), ( float(data[-1]['Close']) - float(data[0]['Close']))/len(data) ) )
    
# 19	592.12	11,250.28	480.00	
def get_f( units, avg_price, curr_price ):
    return lambda x:(units*avg_price + curr_price*x)/( units + x )

