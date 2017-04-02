
// Author : Prashant Srivastava ( _P0W! )
// Dated  : January 1st, 2017
// Last Modified : April 2nd, 2017

// Note : Function ProcessStocks() is triggered everyday around 5-6 PM IST

function encode_utf8( s )
{
  
  return unescape( encodeURIComponent( s ) );
}

// Simple Moving Average
function SMA( data, startRow , period   )
{
    var tot = 0.0;
  
    for (var i = startRow ; i <=period; i++ )
    {
      tot += data[i]['Close'];
      
    }
   
    return tot/period;
}

// Exponential Moving Average
function EMA( data,  startRow , period  )
{
    var index = period - 1;
    if ( startRow == 0 )
    {
        data[ index + startRow  ]['EMA'] =  SMA( data, 0, period ) ;
    }
    else
    {
        factor = 2.0 / ( period + 1 );
        data[ index + startRow]['EMA'] = ( data[ index + startRow ]['Close'] -  data[ index + startRow -1]['EMA'] ) * factor + data[ index + startRow -1 ]['EMA'] ;
        data[ index + startRow]['AboveEMA'] =   data[ index + startRow ]['Close'] > data[ index + startRow]['EMA'] ;
    }   
}

// Percentage of time, the closing value was above 200 Day EMA
function BullishScore( data,period  )
{
    var tot = 0.0;
    for ( var x = period-1 ; x < data.length; x++ )
    {
      tot += data[x]['AboveEMA'] ;
    }
                                
                                
    return ( 100.0 * tot/( data.length - period  ) ) ;
}   

// Sum of square of n natural numbers
function sum_n_sq( n )
{
    return n*( n + 1 )*( 2*n + 1 )/6.0 ;
}

// Sum of n natural numbers
function sum_n( n )
{
    return n*( n + 1 )/2.0 ;
}

function Analyze( url ) 
{ 
  var period = 200;            
  var response = UrlFetchApp.fetch(url);
  var data = encode_utf8(response.getContentText().toString());   
    
  
  //Logger.log( "RESPONSE " + response.getResponseCode() + data ); 
  
  var csvData = Utilities.parseCsv(data, ",");
  var stockData = [];
  
  // Push in reverse order, skip last column ( header column )
  for (var i = csvData.length - 1 ; i >= 1; i-- )
  {
    
    var d = { 'Date':csvData[i][0], 
              'Close': parseFloat(csvData[i][6]), // 'Close' from here on will be the adjusted close
              'LastTraded': parseFloat(csvData[i][4]), 
              'EMA':0.0,
              'Ratio':0.0,
              'AboveEMA':0 
            }
    stockData.push(d) ;
  }
  
  
  
  for ( var row = 0; row <= stockData.length - period ; row++   )
  {
    EMA( stockData, row, period );
  }
  
  // Regression Analysis
    var close_sum = 0.0;
    var close_square = 0.0;
    var close_sum_square = 0.0;
    var close_date_sum = 0.0;
    var  min_close = stockData[0]['Close'] ;
    var  max_close = 0.0;
  
    for ( var i = 0 ; i < stockData.length; i++ )
    {
        close_sum +=  stockData[i]['Close'] ;
        close_sum_square +=  Math.pow(stockData[i]['Close'],2) ;
        close_date_sum += ( i + 1 ) *  stockData[i]['Close'];
      
        if ( min_close > stockData[i]['Close'] )
        {
            min_close = stockData[i]['Close'];
        }
        if ( max_close < stockData[i]['Close'] )
        {
            max_close = stockData[i]['Close'];
        }
    }
    n = stockData.length;
  
    
    var slope =  ( n*close_date_sum - sum_n( n )*close_sum ) / ( n*sum_n_sq(n) - Math.pow( sum_n(n) , 2 )  );
    var angle = Math.atan( slope ) * 180.0/Math.PI ;
  
    var r = ( n*close_date_sum - sum_n( n )*close_sum   ) / 
            (  Math.sqrt
             ( 
               ( n*sum_n_sq(n) - Math.pow( sum_n(n), 2 ) ) * 
               ( n*close_sum_square  - Math.pow(close_sum, 2) ) 
             ) 
            ) ;

  return { 
    'BullishScore':parseFloat(BullishScore( stockData , period )).toFixed(2),
      'Rate':parseFloat(( stockData[n-1]['Close'] - stockData[0]['Close'] )/n).toFixed(2) ,
        'Angle':parseFloat(angle).toFixed(2),
          'Coeff':parseFloat(r).toFixed(2),
            'Min_Dev':parseFloat(( stockData[n-1]['Close'] - min_close )*100/stockData[n-1]['Close'] ).toFixed(2),
              'Max_Dev':parseFloat(( -stockData[n-1]['Close'] + max_close )*100/max_close).toFixed(2) ,
               'LastTraded':parseFloat( stockData[n-1]['LastTraded'] ).toFixed(2),
        } ; 
  
  
}

function UpdateSheet( sheet, values, a,b,c,d,e,f, errorMessage )
{
  var row = 1;
 
  while ( values[row][0] != "" ) 
  {
    
    var url = 'http://chart.finance.yahoo.com/table.csv?s=' + values[row][0] + '.BO&a=' + a + '&b=' + b + '&c=' + c + '&d=' + d + '&e=' + e + '&f=' + f + '&g=d&ignore=.csv'; 
  
    
    
    /*Logger.log("Stock :%s Bullish :%s Rate:%s Angle:%s Coeff:%s Min_Dev:%s Max_Dev:%s ", 
               values[row][0],
               results['BullishScore'],
               results['Rate'],
               results['Angle'],
               results['Coeff'],
               results['Min_Dev'],
               results['Max_Dev'] );
               */
    row++;
    try
    {
      var results = Analyze( url );
    //One Based
      sheet.getRange(row, 2).setValue( results['BullishScore'] ) ;
      sheet.getRange(row, 3).setValue( results['Rate'] ) ;
      sheet.getRange(row, 4).setValue( results['Angle'] ) ;
      sheet.getRange(row, 5).setValue( results['Coeff'] ) ;
      sheet.getRange(row, 6).setValue( results['Min_Dev'] ) ;
      sheet.getRange(row, 7).setValue( results['Max_Dev'] ) ;
      sheet.getRange(row, 8).setValue( results['LastTraded'] ) ;
    }
    catch (err)
    {
      errorMessage += 'Error Fetching ' + values[row][0] + '\n' ;
    }
   
  }
   
  // Update Timestamp, this sucks, 13 is hard coded :|
   sheet.getRange(1, 13).setValue( new Date().toString() ) ;  
}


function ProcessStocks()
{
  var today = new Date();
  var d = today.getMonth() ; //January is 0!
  var e = today.getDate();
  var f = today.getFullYear();
  
  var FiveYearBack = today;
  FiveYearBack.setFullYear( FiveYearBack.getFullYear() - 5 ); // Last 5 year data
  var a = FiveYearBack.getMonth() ;
  var b = FiveYearBack.getDate();
  var c = FiveYearBack.getFullYear();  
  
    
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("S&P BSE Index A Stocks");
  var column = sheet.getRange('A:A');
  var values = column.getValues(); // get all data in one call
  
  var errorMessage = '';
  
  UpdateSheet( sheet, values, a,b,c,d,e,f, errorMessage );
  
  var sheet = ss.getSheetByName("S&P BSE Index B Stocks");
  var column = sheet.getRange('A:A');
  var values = column.getValues(); // get all data in one call
  
  UpdateSheet( sheet, values, a,b,c,d,e,f, errorMessage );
  
  if( errorMessage != '' )
  {
    MailApp.sendEmail("powprashant@gmail.com", "Analysis Script Failure on : " + new Date().toJSON().slice(0,10).replace(/-/g,'/') , errorMessage  ) ;
  }
  
}

// Can be used as formula =getLastTradedPrice('INFY')
// Returns stock value on BSE fr given symbol
function  getLastTradedPrice( symbol  )
{
  var today = new Date();
  var d = today.getMonth() ; //January is 0!
  var e = today.getDate();
  var f = today.getFullYear();
  
  var FiveYearBack = today;
  FiveYearBack.setFullYear( FiveYearBack.getFullYear() - 1 ); // Last 1 year data
  var a = FiveYearBack.getMonth() ;
  var b = FiveYearBack.getDate();
  var c = FiveYearBack.getFullYear(); 
  
  var url = 'http://chart.finance.yahoo.com/table.csv?s=' + symbol + '.BO&a=' + a + '&b=' + b + '&c=' + c + '&d=' + d + '&e=' + e + '&f=' + f + '&g=d&ignore=.csv'; 
   
  
  var response = UrlFetchApp.fetch(url);
  var data = encode_utf8(response.getContentText().toString());   
  var csvData = Utilities.parseCsv(data, ",");
  
  return parseFloat(csvData[1][4]).toFixed(2);
}