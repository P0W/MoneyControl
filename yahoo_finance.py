
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
    return sum( x['Close'] for x in data[startRow:(period)] )/period

def BullishScore( data,period = 200 ):
    return '%.2f' % ( 100.0 * sum( x['AboveEMA'] for x in data[period-1: len(data) ] )/( len(data) - period  ) )
    
def EMA( data,  startRow = 0, period = 200 ):
    index = period - 1
    if startRow == 0:
        data[ index + startRow  ]['EMA'] =  SMA( data, 0, period )
    else:
        factor = 2.0 / ( period + 1 )
        data[ index + startRow]['EMA'] = ( data[ index + startRow ]['Close'] -  data[ index + startRow -1]['EMA'] ) * factor + data[ index + startRow -1 ]['EMA']
        data[ index + startRow]['AboveEMA'] =   data[ index + startRow ]['Close'] > data[ index + startRow]['EMA'] 

def fixSplitShare( data ):
    splitRatio = 1.0
    for i in range(len(data[1:])):
        data[i]['Close'] = data[i]['Close'] / splitRatio
        if data[i-1]['Close'] !=0:
            ratio = data[i]['Close']/data[i-1]['Close']
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
    csvFileName = r"C:/temp/stocks"  + "/" + ticker_symbol + ".csv"
    x = { 'symbol':ticker_symbol, 'fromDate':fromDate, 'toDate':toDate , 'csvFileName' :csvFileName }
    try:
        urlretrieve( base_url % x , x['csvFileName'] )
    except ContentTooShortError as e:
        print ( str(e) )
        pass


    with open( x['csvFileName'],'r') as fin: 
        dr = csv.DictReader(fin) 
        to_db = [ { 'Date':i['Date'], 'Close': float(i['Adj Close']), 'EMA':0.0, 'Ratio':0.0, 'AboveEMA':0 } for i in dr]

    #fixSplitShare( to_db )
    to_db = sorted( to_db, key=lambda k: k['Date'])
    
                   
    for row in range(0, len(to_db) - period + 1   ):
        EMA( to_db, row, period )
    
    return to_db


SP_BSE_ALL_INDEX_A =[
'ABAN',
'ABB',
'ABIRLANUVO',
'ACC',
'ADANIENT',
'ADANIPORTS',
'ADANIPOWER',
'AIAENG',
'AJANTPHARM',
'ALBK',
'ALOKTEXT',
'AMARAJABAT',
'AMBUJACEM',
'AMTEKAUTO',
'ANDHRABANK',
'APLLTD',
'APOLLOHOSP',
'APOLLOTYRE',
'ARVIND',
'ASHOKLEY',
'ASIANPAINT',
'ATUL',
'AUROPHARMA',
'AXISBANK',
##'BAJAJ-AUTO', ## yahoo finance symbol issue ???
'BAJAJELEC',
'BAJAJFINSV',
'BAJAJHLDNG',
'BAJFINANCE',
'BALKRISIND',
'BALRAMCHIN',
'BANKBARODA',
'BANKINDIA',
'BATAINDIA',
'BAYERCROP',
'BEL',
'BEML',
'BERGEPAINT',
'BFUTILITIE',
'BHARATFIN',
'BHARATFORG',
'BHARTIARTL',
'BHEL',
'BIOCON',
'BLUEDART',
'BOSCHLTD',
'BPCL',
'BRITANNIA',
'CADILAHC',
'CAIRN',
'CANBK',
'CARERATING',
'CASTROLIND',
'CEATLTD',
'CENTRALBK',
'CENTURYTEX',
'CESC',
'CHOLAFIN',
'CIPLA',
'COALINDIA',
'COLPAL',
'CONCOR',
'COROMANDEL',
'CORPBANK',
'COX&KINGS',
'CRISIL',
'CROMPGREAV',
'CUB',
'CUMMINSIND',
'CYIENT',
'DABUR',
'DCBBANK',
'DELTACORP',
'DEN',
'DENABANK',
'DHFL',
'DISHTV',
'DIVISLAB',
'DLF',
'DRREDDY',
'ECLERX',
'EDELWEISS',
'EICHERMOT',
'EIDPARRY',
'EMAMILTD',
'ENGINERSIN',
'ESCORTS',
'EXIDEIND',
'FEDERALBNK',
'FINCABLES',
'FINOLEXIND',
'FORTIS',
'FSL',
'GAIL',
'GATI',
'GDL',
'GESHIP',
'GET&D',
'GLAXO',
'GLENMARK',
'GMDCLTD',
'GMRINFRA',
'GODREJCP',
'GODREJIND',
'GODREJPROP',
'GPPL',
'GRASIM',
'GRUH',
'GSFC',
'GSKCONS',
'GSPL',
'GVKPIL',
'HATHWAY',
'HAVELLS',
'HCC',
'HCLTECH',
'HDFC',
'HDFCBANK',
'HDIL',
'HEROMOTOCO',
'HEXAWARE',
'HINDALCO',
'HINDCOPPER',
'HINDPETRO',
'HINDUNILVR',
##'IBREALEST*', ## yahoo finance symbol issue ???
'IBULHSGFIN',
'ICICIBANK',
'IDBI',
'IDEA',
'IDFC',
'IFCI',
'IGL',
'IIFL',
'IL&FSTRANS',
'INDHOTEL',
'INDIACEM',
'INDIANB',
'INDUSINDBK',
'INFRATEL',
'INFY',
'INTELLECT',
'IOB',
'IOC',
'IPCALAB',
'IRB',
'ITC',
'J&KBANK',
'JETAIRWAYS',
'JINDALSTEL',
'JISLJALEQS',
'JKLAKSHMI',
'JKTYRE',
'JPASSOCIAT',
'JPINFRATEC',
'JPPOWER',
'JSWENERGY',
'JSWSTEEL',
'JUBILANT',
'JUBLFOOD',
'JUSTDIAL',
'KAJARIACER',
'KANSAINER',
'KEC',
'KOTAKBANK',
'KPIT',
'KSCL',
'KTKBANK',
'L&TFH',
'LAXMIMACH',
'LICHSGFIN',
'LT',
'LUPIN',
'M&M',
'M&MFIN',
'MANAPPURAM',
'MARICO',
'MARKSANS',
'MARUTI',
'MCLEODRUSS',
'MFSL',
'MINDTREE',
'MMTC',
'MONSANTO',
'MOTHERSUMI',
'MPHASIS',
'MRF',
'MRPL',
'MUTHOOTFIN',
'NATCOPHARM',
'NATIONALUM',
'NAUKRI',
'NCC',
'NESTLEIND',
'NETWORK18',
'NHPC',
'NIITTECH',
'NLCINDIA',
'NMDC',
'NTPC',
'OBEROIRLTY',
'OFSS',
'OIL',
'ONGC',
'ORIENTBANK',
'PAGEIND',
'PCJEWELLER',
'PEL',
'PERSISTENT',
'PETRONET',
'PFC',
'PFIZER',
'PGHH',
'PIDILITIND',
'PIIND',
'PNB',
'POLARIS',
'POWERGRID',
'PRESTIGE',
'PTC',
'PUNJLLOYD',
'PVR',
'RAJESHEXPO',
'RALLIS',
'RAMCOCEM',
'RAYMOND',
'RCOM',
'RDEL',
'RECLTD',
'REDINGTON',
'RELCAPITAL',
'RELIANCE',
'RELINFRA',
'RENUKA',
'REPCOHOME',
'RPOWER',
'RTNPOWER',
'SADBHAV',
'SAIL',
'SANOFI',
'SBIN',
'SCI',
'SHREECEM',
'SIEMENS',
'SINTEX',
'SJVN',
'SKFINDIA',
'SOBHA',
'SOUTHBANK',
'SPARC',
'SREINFRA',
'SRF',
'SRTRANSFIN',
'STAR',
'SUNPHARMA',
'SUNTV',
'SUPREMEIND',
'SUZLON',
'SYNDIBANK',
'TATACHEM',
'TATACOMM',
'TATAELXSI',
'TATAGLOBAL',
'TATAMOTORS',
'TATAPOWER',
'TATASTEEL',
'TCS',
'TECHM',
'THERMAX',
'TITAN',
'TORNTPHARM',
'TORNTPOWER',
'TRENT',
'TTKPRESTIG',
'TUBEINVEST',
'TV18BRDCST',
'TVSMOTOR',
'UBL',
'UCOBANK',
'ULTRACEMCO',
'UNIONBANK',
'UNITDSPR',
'UNITECH',
'UPL',
'VAKRANGEE',
'VEDL',
'VIDEOIND',
'VOLTAS',
'VRLLOG',
'WABAG',
'WELCORP',
'WIPRO',
'WOCKPHARMA',
'YESBANK',
'ZEEL',
]


def sum_n_sq( n ):
    return n*( n + 1 )*( 2*n + 1 )/6.0

def sum_n( n ):
    return n*( n + 1 )/2.0


for s in SP_BSE_ALL_INDEX_A:
    data = pull_historical_data('%s.BO' % s, 200, 5 )
    
    close_sum = 0.0
    close_square = 0.0
    close_sum_square = 0.0
    close_date_sum = 0.0
    min_close = data[0]['Close']
    max_close = 0.0
    for i,x in enumerate(data):
        close_sum +=  x['Close'] 
        close_sum_square +=  x['Close']  * x['Close'] 
        close_date_sum += ( i + 1 ) *  x['Close']
        if min_close > x['Close'] :
            min_close = x['Close']
        if max_close < x['Close'] :
            max_close = x['Close']
        
    n = len(data)
    slope =  ( n*close_date_sum - sum_n( n )*close_sum ) / ( n*sum_n_sq(n) - sum_n(n)**2 )
    angle = math.atan( slope ) * 180.0/math.pi

    #print ( '%-20s is %s %% Bullish with Increase rate of %.2f Slope = %.2f degrees' % ( s, BullishScore( data ), ( float(data[-1]['Close']) - float(data[0]['Close']))/len(data), angle ) )
    print ( '%-20s\t%s\t%.2f\t%.2f\t%.2f\t%.2f' % ( s, BullishScore( data ), ( data[-1]['Close'] - data[0]['Close'] )/n, angle,
                                                    ( data[-1]['Close'] - min_close )*100/data[-1]['Close'] ,
                                                    ( -data[-1]['Close'] + max_close )*100/max_close ) )

    
# 19	592.12	11,250.28	480.00	
def get_f( units, avg_price, curr_price ):
    return lambda x:(units*avg_price + curr_price*x)/( units + x )

