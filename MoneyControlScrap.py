## Author : Prashant
## Grab stocks data from MoneyControl.com

##1. Zero Debt
##2. More percentage of Cash Flow to Market Cap 
##3. Zero ShareHolder Stake Pledge
##4. Large Profit
##5. Less Competition


from bs4 import BeautifulSoup
from urllib.request import *
import re
import sqlite3
import csv

class UrlOpener( object ):
    def __init__(self, url):
        proxy = ProxyHandler({'http': 'http://approxy.rockwellcollins.com:9090'})
        opener = build_opener(proxy)
        install_opener(opener)
        self.url = url

    def contents(self):
        return BeautifulSoup( urlopen(self.url), "html.parser" )


class StockDB( object ):
    def __init__(self):
        self.connector = sqlite3.connect('stocks.db')
        self.cursor = self.connector.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS
                 STOCKSDATA
                (
                Company TEXT PRIMARY KEY NOT NULL,
                Market_Cap REAL NOT NULL,
                Total_Debt REAL NOT NULL,
                Total_Asset REAL NOT NULL,
                Cash_Flow REAL NOT NULL,
                Cash_to_Market REAL NOT NULL,
                Pomoters_Stake_Pledged TEXT NOT NULL,
                Net_Profit REAL NOT NULL,
                Sector TEXT NOT NULL
                );''')
        
        self.connector.commit()

    def writeData(self, values):
        try:
            self.cursor.execute("""
            INSERT INTO
                STOCKSDATA
                ( Company, Market_Cap, Total_Debt, Total_Asset, Cash_Flow, Cash_to_Market, Pomoters_Stake_Pledged, Net_Profit, Sector )
                VALUES( ?,?,?,?,?,?,?,?,? );
                """, values)

            self.connector.commit()
        except sqlite3.IntegrityError:
            print ('      Already Exists Skipped...')

    def displayData(self, sortBY = 'Total_Debt', order = '' ):
        for row in self.cursor.execute("SELECT * FROM STOCKSDATA ORDER BY %s %s;" % (sortBY, order )
                                        ):
            print (row)

    def companyList(self):
        res = []
        for row in self.cursor.execute('SELECT Company FROM STOCKSDATA ORDER BY Company'):
            res.append( row[0] )
        return res
    
    def __del__(self):
        print ('Closing Database')
        self.cursor.close()
        self.connector.close()

    def export(self, csvFile = 'stocks.csv', sortBY = 'Total_Debt', order = '' ):
        self.cursor.execute('''SELECT Sector, Company, Market_Cap, Total_Asset, Cash_Flow, Net_Profit FROM STOCKSDATA \
                            WHERE Pomoters_Stake_Pledged LIKE 'FALSE' AND Cash_to_Market > 0 AND Net_Profit>0 \
                            AND Total_Debt = 0  AND Total_Asset > 0 \
                            ORDER BY  Sector ASC, \
                                      Total_Debt ASC, \
                                      Net_Profit DESC ,\
                                      Cash_to_Market DESC ,\
                                      Total_Asset DESC''' \
                                        )
        with open( csvFile, "w", newline='') as csv_file:  
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in self.cursor.description]) 
            csv_writer.writerows(self.cursor)

def ReadCashFlow( url ):
    soup =  UrlOpener( url ).contents()
    try:
        return soup.find(text='Closing Cash & Cash Equivalents').findNext().get_text()
    except AttributeError:
        return '0.0'
    except Exception as e:
        print (str(e))
        return '0.0'


def isPromotersStakePledged( url ):
    # <table width="100%" border="0" class="b_12 dvdtbl" cellspacing="0" cellpadding="0">
    soup =  UrlOpener( url ).contents()
    try:
        
        rows = soup.find("table", {"class":"b_12 dvdtbl"} ).find_all("tr")
        for row in rows[2:]:
            cells = row.find_all("td")
            for cell in cells[-1:]:
                if  '-' not in cell.get_text():
                    print (cell.get_text())
                    return True
    except AttributeError:
        return True
    except Exception as e:
        print (str(e))
        return False    
    return False
    

def GrabStocks():
    DB = StockDB()
    test_sufix = '.+' # 'auto-cars-jeeps' # 'chemicals' # 'cement-major' # 'computers-software' # 'auto-cars-jeeps' #
    soup = UrlOpener( r'http://www.moneycontrol.com/stocks/sectors/'  ).contents()
    scrapPattern_0 = soup("a", {  'href':re.compile(r'/stocks/sectors/%s\.html$' % test_sufix) })
    visited = {}
    companyList = DB.companyList()
    
    for sites in scrapPattern_0:
        
        soup = UrlOpener( sites['href'] ).contents()
        
        scrapPattern_1 = soup("a", {  'href':re.compile(r'/stockpricequote/.+/.+') })
        
        if scrapPattern_1:

            print ( 'Listing all companies from %s Sector' % sites.get_text() )
        for stocks in scrapPattern_1:

            compName = stocks.get_text()
            
            if compName in visited  :continue
            elif compName in companyList: continue
            else: visited[ stocks.get_text() ] =''

            print ( '--- %s' % stocks.get_text() )
            
            soup = UrlOpener( r'http://www.moneycontrol.com/%s' % stocks['href'] ).contents()

            try:
                cashflowUrl = r'http://www.moneycontrol.com/%s' % ( soup.findAll(text='Cash Flow')[1].findPrevious()['href'] )
                Cash_Flow =  float(ReadCashFlow( cashflowUrl ).replace(',', '' ))
            except:
                Cash_Flow = 0.0

            try:
                sharesPledgedByPromotersUrl = r'http://www.moneycontrol.com/%s' % soup.find(text='Shares Pledged by Promoters').findParent()['href']
                isStakePledged = isPromotersStakePledged( sharesPledgedByPromotersUrl )
            except:
                isStakePledged = True

            try:      
                Market_Cap = soup.find(text='MARKET CAP (Rs Cr)').findNext().get_text(),
                Market_Cap = float(Market_Cap[0].replace(',',''))
                Total_Debt =  float( soup.find(text='Total Debt').findNext().get_text().replace(',', '' ) )
                Total_Asset = float(  soup.findAll(text='Total Assets')[1].findNext().get_text().replace(',', '' ) )
                Cash_to_Market_cap_ratio = 100.0*Cash_Flow  /  Market_Cap
                Net_Profit = soup.find('td', text=re.compile("Net Profit"), attrs={'class' : 'thc02 w160 gD_12'}).findNext().get_text()
                Net_Profit = float( Net_Profit.replace(',','') )
            except:
                Market_Cap = 1.0
                Total_Debt = 0.0
                Total_Asset = 0.0
                Cash_to_Market_cap_ratio = 0.0
                Net_Profit = 0.0

            values = [
            stocks.get_text(),
             Market_Cap ,
             Total_Debt, ## Total Debt
             Total_Asset, ## Total Asset
             Cash_Flow,
             Cash_to_Market_cap_ratio,
             '%s' % isStakePledged,
            Net_Profit,
            sites.get_text()
            ]        
            DB.writeData( values )
       

def Display( sortBy = 'Total_Debt', order ='' ):            
    StockDB().displayData( sortBy, order )

        



